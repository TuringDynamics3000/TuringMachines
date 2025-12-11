"""
db.py — Unified database engine for TuringMachines (async + sync)
------------------------------------------------------------------

This module provides:

✔ Async SQLAlchemy engine (default)
✔ Sync SQLAlchemy engine (fallback)
✔ pgvector extension registration
✔ Session factories for both modes
✔ Automatic engine selection via DB_MODE env var
✔ FastAPI lifecycle hooks (init_db / close_db)

DB Modes:
    DB_MODE=async   → asyncpg + async SQLAlchemy (recommended)
    DB_MODE=sync    → psycopg2 sync fallback

"""

import os
import logging
from typing import Optional, AsyncGenerator, Generator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from sqlalchemy.orm import (
    sessionmaker,
    Session,
    declarative_base,
)

from sqlalchemy import text, create_engine

# --------------------------------------------
# Configuration
# --------------------------------------------

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres@localhost:5432/turingcapture"
)

DB_MODE = os.getenv("DB_MODE", "async").lower()  # async | sync

logger = logging.getLogger("turing.db")
logger.setLevel(logging.INFO)

Base = declarative_base()

# Engines (created lazily)
_async_engine = None
_sync_engine = None

_async_session_factory: Optional[async_sessionmaker] = None
_sync_session_factory: Optional[sessionmaker] = None


# --------------------------------------------
# ENGINE CREATION
# --------------------------------------------

def create_sync_engine():
    """Create a synchronous SQLAlchemy engine (psycopg2)."""

    global _sync_engine, _sync_session_factory

    if "+asyncpg" in DATABASE_URL:
        # Convert URL to synchronous driver format
        sync_url = DATABASE_URL.replace("+asyncpg", "")
    else:
        sync_url = DATABASE_URL

    logger.info(f"[DB] Creating SYNC engine: {sync_url}")

    _sync_engine = create_engine(
        sync_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=False,
        future=True
    )

    _sync_session_factory = sessionmaker(
        bind=_sync_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        class_=Session
    )


def create_async_engine_wrapper():
    """Create an asynchronous SQLAlchemy engine (asyncpg)."""

    global _async_engine, _async_session_factory

    if "+asyncpg" not in DATABASE_URL:
        async_url = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    else:
        async_url = DATABASE_URL

    logger.info(f"[DB] Creating ASYNC engine: {async_url}")

    _async_engine = create_async_engine(
        async_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=False,
        future=True
    )

    _async_session_factory = async_sessionmaker(
        bind=_async_engine,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
        class_=AsyncSession,
    )


# --------------------------------------------
# INITIALIZATION & SHUTDOWN
# --------------------------------------------

async def init_db():
    """
    Called at FastAPI startup to initialize the DB and ensure pgvector is ready.
    """
    logger.info(f"[DB] Initializing database ({DB_MODE} mode)…")

    if DB_MODE == "async":
        create_async_engine_wrapper()
        await register_vector_extension_async()
    else:
        create_sync_engine()
        register_vector_extension_sync()

    logger.info("[DB] Initialization complete.")


async def close_db():
    """Graceful async shutdown."""
    if DB_MODE == "async" and _async_engine:
        logger.info("[DB] Closing async engine…")
        await _async_engine.dispose()


# --------------------------------------------
# PGVECTOR EXTENSION
# --------------------------------------------

async def register_vector_extension_async():
    """Create pgvector extension (async)."""
    try:
        async with _async_engine.begin() as conn:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        logger.info("[DB] pgvector extension ensured (async).")
    except Exception as e:
        logger.warning(f"[DB] Could not create pgvector extension: {e}")
        logger.warning("[DB] Continuing without pgvector (embeddings will not be stored)")


def register_vector_extension_sync():
    """Create pgvector extension (sync)."""
    try:
        with _sync_engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        logger.info("[DB] pgvector extension ensured (sync).")
    except Exception as e:
        logger.warning(f"[DB] Could not create pgvector extension: {e}")
        logger.warning("[DB] Continuing without pgvector (embeddings will not be stored)")


# --------------------------------------------
# SESSION HELPERS
# --------------------------------------------

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that returns an async DB session.
    """
    if _async_session_factory is None:
        raise RuntimeError("Async DB engine not initialized. Call init_db().")

    async with _async_session_factory() as session:
        yield session


def get_sync_session() -> Generator[Session, None, None]:
    """
    Synchronous session for fallback or offline tools.
    """
    if _sync_session_factory is None:
        raise RuntimeError("Sync DB engine not initialized. Call init_db().")

    with _sync_session_factory() as session:
        yield session


# --------------------------------------------
# UNIVERSAL EXECUTION HELPERS
# --------------------------------------------

async def execute_async(query, params=None):
    """Execute SQL asynchronously."""
    async with _async_session_factory() as session:
        result = await session.execute(query, params or {})
        await session.commit()
        return result


def execute_sync(query, params=None):
    """Execute SQL synchronously."""
    with _sync_session_factory() as session:
        result = session.execute(query, params or {})
        session.commit()
        return result


# --------------------------------------------
# MODE-BASED DISPATCH
# --------------------------------------------

async def save_record_async(record):
    async with _async_session_factory() as session:
        session.add(record)
        await session.commit()
        await session.refresh(record)
        return record


def save_record_sync(record):
    with _sync_session_factory() as session:
        session.add(record)
        session.commit()
        session.refresh(record)
        return record


async def save_record(record):
    """Unified save method that supports async/sync based on DB_MODE."""
    if DB_MODE == "async":
        return await save_record_async(record)
    else:
        return save_record_sync(record)
