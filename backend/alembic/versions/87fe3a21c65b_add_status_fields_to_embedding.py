"""Add status fields to embedding

Revision ID: 87fe3a21c65b
Revises: 41e25ffba876
Create Date: 2025-03-27 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '87fe3a21c65b'
down_revision = '41e25ffba876'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to embeddings table
    op.add_column('embeddings', sa.Column('status', sa.String(), nullable=True))
    op.add_column('embeddings', sa.Column('error', sa.Text(), nullable=True))
    op.add_column('embeddings', sa.Column('completed_at', sa.DateTime(), nullable=True))
    
    # Create index on status column
    op.create_index(op.f('ix_embeddings_status'), 'embeddings', ['status'], unique=False)
    
    # Update existing rows to have 'completed' status
    op.execute("UPDATE embeddings SET status = 'completed' WHERE status IS NULL")
    
    # Make status column not nullable
    op.alter_column('embeddings', 'status', nullable=False)


def downgrade():
    # Drop the new columns
    op.drop_index(op.f('ix_embeddings_status'), table_name='embeddings')
    op.drop_column('embeddings', 'completed_at')
    op.drop_column('embeddings', 'error')
    op.drop_column('embeddings', 'status')
