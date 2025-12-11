"""Initial biometrics schema

Revision ID: 001
Revises: 
Create Date: 2024-12-11 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create biometric_sessions table
    op.create_table(
        'biometric_sessions',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('tenant_id', sa.String(length=64), nullable=False),
        sa.Column('user_id', sa.String(length=64), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('liveness_passed', sa.Boolean(), nullable=True),
        sa.Column('face_match_passed', sa.Boolean(), nullable=True),
        sa.Column('overall_risk_level', sa.String(length=16), nullable=True),
        sa.Column('extra_metadata', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_session_tenant_created', 'biometric_sessions', ['tenant_id', 'created_at'])
    op.create_index('idx_session_status', 'biometric_sessions', ['status'])
    op.create_index(op.f('ix_biometric_sessions_tenant_id'), 'biometric_sessions', ['tenant_id'])
    op.create_index(op.f('ix_biometric_sessions_user_id'), 'biometric_sessions', ['user_id'])
    
    # Create biometric_artifacts table
    op.create_table(
        'biometric_artifacts',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('session_id', sa.String(length=64), nullable=False),
        sa.Column('artifact_type', sa.String(length=32), nullable=False),
        sa.Column('storage_mode', sa.String(length=16), nullable=False),
        sa.Column('storage_path', sa.Text(), nullable=True),
        sa.Column('image_format', sa.String(length=16), nullable=True),
        sa.Column('image_size_bytes', sa.Integer(), nullable=True),
        sa.Column('image_width', sa.Integer(), nullable=True),
        sa.Column('image_height', sa.Integer(), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('blur_score', sa.Float(), nullable=True),
        sa.Column('brightness_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('extra_metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['biometric_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_artifact_session_type', 'biometric_artifacts', ['session_id', 'artifact_type'])
    op.create_index(op.f('ix_biometric_artifacts_session_id'), 'biometric_artifacts', ['session_id'])
    
    # Create liveness_results table
    op.create_table(
        'liveness_results',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('session_id', sa.String(length=64), nullable=False),
        sa.Column('artifact_id', sa.String(length=64), nullable=True),
        sa.Column('liveness_score', sa.Float(), nullable=False),
        sa.Column('blink_score', sa.Float(), nullable=True),
        sa.Column('motion_score', sa.Float(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('face_centered', sa.Boolean(), nullable=True),
        sa.Column('face_size', sa.Float(), nullable=True),
        sa.Column('liveness_engine', sa.String(length=32), nullable=False),
        sa.Column('liveness_version', sa.String(length=16), nullable=True),
        sa.Column('passed', sa.Boolean(), nullable=False),
        sa.Column('risk_level', sa.String(length=16), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('extra_metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['artifact_id'], ['biometric_artifacts.id'], ),
        sa.ForeignKeyConstraint(['session_id'], ['biometric_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_liveness_session', 'liveness_results', ['session_id'])
    op.create_index('idx_liveness_passed', 'liveness_results', ['passed'])
    op.create_index(op.f('ix_liveness_results_session_id'), 'liveness_results', ['session_id'])
    
    # Create face_embeddings table
    op.create_table(
        'face_embeddings',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('session_id', sa.String(length=64), nullable=False),
        sa.Column('artifact_id', sa.String(length=64), nullable=True),
        sa.Column('embedding_type', sa.String(length=32), nullable=False),
        sa.Column('model_name', sa.String(length=32), nullable=False),
        sa.Column('embedding_size', sa.Integer(), nullable=False),
        # Use JSON for embedding_vector (pgvector will be added manually if available)
        sa.Column('embedding_vector', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('extra_metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['artifact_id'], ['biometric_artifacts.id'], ),
        sa.ForeignKeyConstraint(['session_id'], ['biometric_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_embedding_session', 'face_embeddings', ['session_id'])
    op.create_index('idx_embedding_type_model', 'face_embeddings', ['embedding_type', 'model_name'])
    op.create_index(op.f('ix_face_embeddings_session_id'), 'face_embeddings', ['session_id'])
    
    # Create face_match_results table
    op.create_table(
        'face_match_results',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('session_id', sa.String(length=64), nullable=False),
        sa.Column('id_embedding_id', sa.String(length=64), nullable=True),
        sa.Column('selfie_embedding_id', sa.String(length=64), nullable=True),
        sa.Column('model_name', sa.String(length=32), nullable=False),
        sa.Column('similarity_score', sa.Float(), nullable=False),
        sa.Column('distance_score', sa.Float(), nullable=True),
        sa.Column('threshold', sa.Float(), nullable=False),
        sa.Column('match', sa.Boolean(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('risk_level', sa.String(length=16), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('extra_metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['id_embedding_id'], ['face_embeddings.id'], ),
        sa.ForeignKeyConstraint(['selfie_embedding_id'], ['face_embeddings.id'], ),
        sa.ForeignKeyConstraint(['session_id'], ['biometric_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_match_session', 'face_match_results', ['session_id'])
    op.create_index('idx_match_result', 'face_match_results', ['match'])
    op.create_index(op.f('ix_face_match_results_session_id'), 'face_match_results', ['session_id'])
    
    # Create biometric_events table
    op.create_table(
        'biometric_events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('session_id', sa.String(length=64), nullable=False),
        sa.Column('event_type', sa.String(length=64), nullable=False),
        sa.Column('event_status', sa.String(length=32), nullable=False),
        sa.Column('event_data', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['biometric_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_event_session_created', 'biometric_events', ['session_id', 'created_at'])
    op.create_index('idx_event_type', 'biometric_events', ['event_type'])
    op.create_index(op.f('ix_biometric_events_session_id'), 'biometric_events', ['session_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('biometric_events')
    op.drop_table('face_match_results')
    op.drop_table('face_embeddings')
    op.drop_table('liveness_results')
    op.drop_table('biometric_artifacts')
    op.drop_table('biometric_sessions')
    
    # Note: We don't drop the vector extension as it might be used by other services
    # op.execute('DROP EXTENSION IF EXISTS vector')
