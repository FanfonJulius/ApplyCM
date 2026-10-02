"""expand schools and programs tables

Revision ID: d578391f7a12
Revises: c467286e6e24
Create Date: 2026-09-26 22:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd578391f7a12'
down_revision = 'c467286e6e24'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Update schools table
    op.add_column('schools', sa.Column('location', sa.String(), nullable=True))
    op.add_column('schools', sa.Column('website_url', sa.String(), nullable=True))
    op.add_column('schools', sa.Column('logo_url', sa.String(), nullable=True))
    op.add_column('schools', sa.Column('contact_email', sa.String(), nullable=True))
    op.add_column('schools', sa.Column('application_deadline', sa.String(), nullable=True))
    op.add_column('schools', sa.Column('rolling_admission', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    
    # Drop legacy columns from schools
    op.drop_column('schools', 'arrondissement')
    op.drop_column('schools', 'city')

    # 2. Update programs table
    op.add_column('programs', sa.Column('degree_type', sa.String(), nullable=True))
    op.add_column('programs', sa.Column('tuition_fee', sa.String(), nullable=True))
    op.add_column('programs', sa.Column('duration', sa.String(), nullable=True))
    op.add_column('programs', sa.Column('language_of_instruction', sa.String(), nullable=True))
    op.add_column('programs', sa.Column('delivery_mode', sa.String(), nullable=True))
    op.add_column('programs', sa.Column('required_documents', sa.Text(), nullable=True))
    op.add_column('programs', sa.Column('application_deadline', sa.String(), nullable=True))
    op.add_column('programs', sa.Column('class_size', sa.Integer(), nullable=True))
    op.add_column('programs', sa.Column('description', sa.Text(), nullable=True))

    # Drop old tuition numeric column
    op.drop_column('programs', 'tuition')


def downgrade() -> None:
    # Revert programs
    op.add_column('programs', sa.Column('tuition', sa.Numeric(12, 2), nullable=True))
    op.drop_column('programs', 'description')
    op.drop_column('programs', 'class_size')
    op.drop_column('programs', 'application_deadline')
    op.drop_column('programs', 'required_documents')
    op.drop_column('programs', 'delivery_mode')
    op.drop_column('programs', 'language_of_instruction')
    op.drop_column('programs', 'duration')
    op.drop_column('programs', 'tuition_fee')
    op.drop_column('programs', 'degree_type')

    # Revert schools
    op.add_column('schools', sa.Column('city', sa.String(), nullable=True))
    op.add_column('schools', sa.Column('arrondissement', sa.String(), nullable=True))
    op.drop_column('schools', 'rolling_admission')
    op.drop_column('schools', 'application_deadline')
    op.drop_column('schools', 'contact_email')
    op.drop_column('schools', 'logo_url')
    op.drop_column('schools', 'website_url')
    op.drop_column('schools', 'location')