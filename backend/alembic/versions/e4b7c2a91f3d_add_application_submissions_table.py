"""add application_submissions table

Revision ID: e4b7c2a91f3d
Revises: d578391f7a12
Create Date: 2026-09-29 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'e4b7c2a91f3d'
down_revision = 'd578391f7a12'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'application_submissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('school_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('recipient_email', sa.String(length=255), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['student_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['school_id'], ['schools.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('student_id', 'school_id', name='uq_application_submissions_student_school'),
    )
    op.create_index('ix_application_submissions_student_id', 'application_submissions', ['student_id'])
    op.create_index('ix_application_submissions_school_id', 'application_submissions', ['school_id'])


def downgrade() -> None:
    op.drop_index('ix_application_submissions_school_id', table_name='application_submissions')
    op.drop_index('ix_application_submissions_student_id', table_name='application_submissions')
    op.drop_table('application_submissions')
