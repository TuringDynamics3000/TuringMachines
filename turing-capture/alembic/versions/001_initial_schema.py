"""Initial biometrics schema

Revision ID: 001
Revises: 
Create Date: 2024-12-11

"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None

def upgrade():
    # Enable pgvector
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create tables
    op.execute('''
        CREATE TABLE biometric_sessions (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            user_id VARCHAR(64),
            status VARCHAR(32) NOT NULL DEFAULT 'created',
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
            completed_at TIMESTAMP,
            liveness_passed BOOLEAN,
            face_match_passed BOOLEAN,
            overall_risk_level VARCHAR(16),
            extra_metadata JSONB
        );
        
        CREATE INDEX idx_session_tenant ON biometric_sessions(tenant_id);
        CREATE INDEX idx_session_status ON biometric_sessions(status);
    ''')

def downgrade():
    op.drop_table('biometric_sessions')
