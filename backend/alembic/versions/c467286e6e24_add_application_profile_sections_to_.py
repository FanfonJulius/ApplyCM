"""add application profile sections to student_profiles

Adds the shared application-profile wizard fields (personal, contact,
education, testing, activities, writing) and relaxes full_name so any wizard
section can be saved first.

Revision ID: c467286e6e24
Revises: 0dd12cfb019b
Create Date: 2026-09-24 10:03:10.296415

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c467286e6e24'
down_revision: Union[str, Sequence[str], None] = '0dd12cfb019b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('student_profiles', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('student_profiles', sa.Column('first_name', sa.String(length=100), nullable=True))
    op.add_column('student_profiles', sa.Column('last_name', sa.String(length=100), nullable=True))
    op.add_column('student_profiles', sa.Column('email', sa.String(length=255), nullable=True))
    op.add_column('student_profiles', sa.Column('declared_state', sa.String(length=100), nullable=True))
    op.add_column('student_profiles', sa.Column('address', sa.String(length=255), nullable=True))
    op.add_column('student_profiles', sa.Column('city', sa.String(length=100), nullable=True))
    op.add_column('student_profiles', sa.Column('region', sa.String(length=100), nullable=True))
    op.add_column('student_profiles', sa.Column('emergency_contact_name', sa.String(length=200), nullable=True))
    op.add_column('student_profiles', sa.Column('emergency_contact_phone', sa.String(length=32), nullable=True))
    op.add_column('student_profiles', sa.Column('secondary_school', sa.String(length=255), nullable=True))
    op.add_column('student_profiles', sa.Column('o_level_slip_url', sa.Text(), nullable=True))
    op.add_column('student_profiles', sa.Column('a_level_slip_url', sa.Text(), nullable=True))
    op.add_column('student_profiles', sa.Column('o_level_passes', sa.String(length=255), nullable=True))
    op.add_column('student_profiles', sa.Column('a_level_points', sa.String(length=255), nullable=True))
    op.add_column('student_profiles', sa.Column('english_test_type', sa.String(length=50), nullable=True))
    op.add_column('student_profiles', sa.Column('english_test_score', sa.String(length=100), nullable=True))
    op.add_column('student_profiles', sa.Column('activity_name', sa.String(length=200), nullable=True))
    op.add_column('student_profiles', sa.Column('activity_role', sa.String(length=200), nullable=True))
    op.add_column('student_profiles', sa.Column('activity_description', sa.Text(), nullable=True))
    op.add_column('student_profiles', sa.Column('honors_awards', sa.Text(), nullable=True))
    op.add_column('student_profiles', sa.Column('essay_prompt', sa.String(length=100), nullable=True))
    op.add_column('student_profiles', sa.Column('additional_info', sa.Text(), nullable=True))
    op.alter_column('student_profiles', 'full_name', existing_type=sa.VARCHAR(), nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("UPDATE student_profiles SET full_name = '' WHERE full_name IS NULL")
    op.alter_column('student_profiles', 'full_name', existing_type=sa.VARCHAR(), nullable=False)
    op.drop_column('student_profiles', 'additional_info')
    op.drop_column('student_profiles', 'essay_prompt')
    op.drop_column('student_profiles', 'honors_awards')
    op.drop_column('student_profiles', 'activity_description')
    op.drop_column('student_profiles', 'activity_role')
    op.drop_column('student_profiles', 'activity_name')
    op.drop_column('student_profiles', 'english_test_score')
    op.drop_column('student_profiles', 'english_test_type')
    op.drop_column('student_profiles', 'a_level_points')
    op.drop_column('student_profiles', 'o_level_passes')
    op.drop_column('student_profiles', 'a_level_slip_url')
    op.drop_column('student_profiles', 'o_level_slip_url')
    op.drop_column('student_profiles', 'secondary_school')
    op.drop_column('student_profiles', 'emergency_contact_phone')
    op.drop_column('student_profiles', 'emergency_contact_name')
    op.drop_column('student_profiles', 'region')
    op.drop_column('student_profiles', 'city')
    op.drop_column('student_profiles', 'address')
    op.drop_column('student_profiles', 'declared_state')
    op.drop_column('student_profiles', 'email')
    op.drop_column('student_profiles', 'last_name')
    op.drop_column('student_profiles', 'first_name')
    op.drop_column('student_profiles', 'updated_at')
