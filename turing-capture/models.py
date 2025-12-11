"""
models.py — SQLAlchemy models for TuringCapture biometrics system
------------------------------------------------------------------

This module defines the database schema for:

✔ BiometricSession - Session tracking
✔ BiometricArtifact - Image storage metadata
✔ LivenessResult - Liveness detection scores
✔ FaceEmbedding - Face embeddings with pgvector
✔ FaceMatchResult - Face matching results
✔ BiometricEvent - Audit log

"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    String,
    Float,
    Boolean,
    Integer,
    DateTime,
    Text,
    JSON,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship

# Import Base from db.py
from db import Base

# pgvector support (optional - gracefully degrades if not available)
try:
    from pgvector.sqlalchemy import Vector
    PGVECTOR_AVAILABLE = True
except ImportError:
    PGVECTOR_AVAILABLE = False
    # Fallback to JSON for embeddings if pgvector not available
    Vector = lambda dim: JSON


# ============================================================================
# BiometricSession
# ============================================================================

class BiometricSession(Base):
    """
    Tracks a biometric verification session
    
    A session represents one complete identity verification flow:
    - ID document capture
    - Selfie capture
    - Liveness detection
    - Face matching
    """
    __tablename__ = "biometric_sessions"
    
    # Primary key
    id = Column(String(64), primary_key=True)  # sess_abc123
    
    # Session metadata
    tenant_id = Column(String(64), nullable=False, index=True, default="default")
    user_id = Column(String(64), nullable=True, index=True)
    
    # Status tracking
    status = Column(String(32), nullable=False, default="created")  # created, in_progress, completed, failed
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Results summary
    liveness_passed = Column(Boolean, nullable=True)
    face_match_passed = Column(Boolean, nullable=True)
    overall_risk_level = Column(String(16), nullable=True)  # low, medium, high, critical
    
    # Metadata
    extra_metadata = Column(JSON, nullable=True)
    
    # Relationships
    artifacts = relationship("BiometricArtifact", back_populates="session", cascade="all, delete-orphan")
    liveness_results = relationship("LivenessResult", back_populates="session", cascade="all, delete-orphan")
    embeddings = relationship("FaceEmbedding", back_populates="session", cascade="all, delete-orphan")
    match_results = relationship("FaceMatchResult", back_populates="session", cascade="all, delete-orphan")
    events = relationship("BiometricEvent", back_populates="session", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_session_tenant_created", "tenant_id", "created_at"),
        Index("idx_session_status", "status"),
    )


# ============================================================================
# BiometricArtifact
# ============================================================================

class BiometricArtifact(Base):
    """
    Stores metadata about biometric images (selfies, ID photos)
    
    Actual images can be stored in:
    - Memory (ephemeral)
    - Local filesystem
    - S3 (production)
    """
    __tablename__ = "biometric_artifacts"
    
    # Primary key
    id = Column(String(64), primary_key=True)  # art_abc123
    
    # Foreign key
    session_id = Column(String(64), ForeignKey("biometric_sessions.id"), nullable=False, index=True)
    
    # Artifact metadata
    artifact_type = Column(String(32), nullable=False)  # selfie, id_front, id_back
    storage_mode = Column(String(16), nullable=False)  # memory, local, s3
    storage_path = Column(Text, nullable=True)  # S3 key or local path
    
    # Image properties
    image_format = Column(String(16), nullable=True)  # jpeg, png
    image_size_bytes = Column(Integer, nullable=True)
    image_width = Column(Integer, nullable=True)
    image_height = Column(Integer, nullable=True)
    
    # Quality metrics
    quality_score = Column(Float, nullable=True)
    blur_score = Column(Float, nullable=True)
    brightness_score = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Metadata
    extra_metadata = Column(JSON, nullable=True)
    
    # Relationships
    session = relationship("BiometricSession", back_populates="artifacts")
    
    # Indexes
    __table_args__ = (
        Index("idx_artifact_session_type", "session_id", "artifact_type"),
    )


# ============================================================================
# LivenessResult
# ============================================================================

class LivenessResult(Base):
    """
    Stores liveness detection results from MediaPipe FaceMesh
    """
    __tablename__ = "liveness_results"
    
    # Primary key
    id = Column(String(64), primary_key=True)  # live_abc123
    
    # Foreign keys
    session_id = Column(String(64), ForeignKey("biometric_sessions.id"), nullable=False, index=True)
    artifact_id = Column(String(64), ForeignKey("biometric_artifacts.id"), nullable=True)
    
    # Liveness scores
    liveness_score = Column(Float, nullable=False)
    blink_score = Column(Float, nullable=True)
    motion_score = Column(Float, nullable=True)
    confidence = Column(Float, nullable=False)
    
    # Detection metadata
    face_centered = Column(Boolean, nullable=True)
    face_size = Column(Float, nullable=True)
    liveness_engine = Column(String(32), nullable=False, default="mediapipe_facemesh")
    liveness_version = Column(String(16), nullable=True)
    
    # Result
    passed = Column(Boolean, nullable=False)
    risk_level = Column(String(16), nullable=True)  # low, medium, high, critical
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Metadata
    extra_metadata = Column(JSON, nullable=True)
    
    # Relationships
    session = relationship("BiometricSession", back_populates="liveness_results")
    
    # Indexes
    __table_args__ = (
        Index("idx_liveness_session", "session_id"),
        Index("idx_liveness_passed", "passed"),
    )


# ============================================================================
# FaceEmbedding
# ============================================================================

class FaceEmbedding(Base):
    """
    Stores face embeddings using pgvector for similarity search
    
    Supports both:
    - MobileFaceNet (128D)
    - ArcFace (512D)
    """
    __tablename__ = "face_embeddings"
    
    # Primary key
    id = Column(String(64), primary_key=True)  # emb_abc123
    
    # Foreign keys
    session_id = Column(String(64), ForeignKey("biometric_sessions.id"), nullable=False, index=True)
    artifact_id = Column(String(64), ForeignKey("biometric_artifacts.id"), nullable=True)
    
    # Embedding metadata
    embedding_type = Column(String(32), nullable=False)  # selfie, id_photo
    model_name = Column(String(32), nullable=False)  # mobilefacenet, arcface
    embedding_size = Column(Integer, nullable=False)  # 128, 512
    
    # Embedding vector (pgvector or JSON fallback)
    if PGVECTOR_AVAILABLE:
        embedding_vector = Column(Vector(512), nullable=False)  # Max size, will work for 128D too
    else:
        embedding_vector = Column(JSON, nullable=False)  # Fallback to JSON array
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Metadata
    extra_metadata = Column(JSON, nullable=True)
    
    # Relationships
    session = relationship("BiometricSession", back_populates="embeddings")
    
    # Indexes
    __table_args__ = (
        Index("idx_embedding_session", "session_id"),
        Index("idx_embedding_type_model", "embedding_type", "model_name"),
    )


# ============================================================================
# FaceMatchResult
# ============================================================================

class FaceMatchResult(Base):
    """
    Stores face matching results (1:1 verification)
    """
    __tablename__ = "face_match_results"
    
    # Primary key
    id = Column(String(64), primary_key=True)  # match_abc123
    
    # Foreign keys
    session_id = Column(String(64), ForeignKey("biometric_sessions.id"), nullable=False, index=True)
    id_embedding_id = Column(String(64), ForeignKey("face_embeddings.id"), nullable=True)
    selfie_embedding_id = Column(String(64), ForeignKey("face_embeddings.id"), nullable=True)
    
    # Match results
    model_name = Column(String(32), nullable=False)  # mobilefacenet, arcface, fusion
    similarity_score = Column(Float, nullable=False)
    distance_score = Column(Float, nullable=True)
    threshold = Column(Float, nullable=False)
    
    # Result
    match = Column(Boolean, nullable=False)
    confidence = Column(Float, nullable=False)
    risk_level = Column(String(16), nullable=True)  # low, medium, high, critical
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Metadata
    extra_metadata = Column(JSON, nullable=True)
    
    # Relationships
    session = relationship("BiometricSession", back_populates="match_results")
    
    # Indexes
    __table_args__ = (
        Index("idx_match_session", "session_id"),
        Index("idx_match_result", "match"),
    )


# ============================================================================
# BiometricEvent
# ============================================================================

class BiometricEvent(Base):
    """
    Audit log for biometric operations
    
    Tracks all events for compliance and debugging:
    - Selfie captured
    - Liveness detected
    - Face matched
    - Session completed
    """
    __tablename__ = "biometric_events"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key
    session_id = Column(String(64), ForeignKey("biometric_sessions.id"), nullable=False, index=True)
    
    # Event metadata
    event_type = Column(String(64), nullable=False)  # selfie_captured, liveness_detected, face_matched
    event_status = Column(String(32), nullable=False)  # success, failure, warning
    
    # Event data
    event_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    session = relationship("BiometricSession", back_populates="events")
    
    # Indexes
    __table_args__ = (
        Index("idx_event_session_created", "session_id", "created_at"),
        Index("idx_event_type", "event_type"),
    )
