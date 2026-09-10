"""Update schema to UUID and enable RLS policies

Revision ID: 0dd12cfb019b
Revises: 0dd12cfb019a
Create Date: 2026-08-19 09:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0dd12cfb019b'
down_revision: Union[str, Sequence[str], None] = '0dd12cfb019a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable required extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

    # 2. Drop old integer tables if they exist
    op.execute("DROP TABLE IF EXISTS favorites CASCADE;")
    op.execute("DROP TABLE IF EXISTS documents CASCADE;")
    op.execute("DROP TABLE IF EXISTS applications CASCADE;")
    op.execute("DROP TABLE IF EXISTS student_profiles CASCADE;")
    op.execute("DROP TABLE IF EXISTS programs CASCADE;")
    op.execute("DROP TABLE IF EXISTS schools CASCADE;")
    op.execute("DROP TABLE IF EXISTS users CASCADE;")

    # 3. Create Users table (UUID)
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=True),
        sa.Column('role', sa.String(), server_default=sa.text("'student'"), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # 4. Create Student Profiles table (UUID)
    op.create_table(
        'student_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('full_name', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('education_summary', sa.Text(), nullable=True),
        sa.Column('writing_sample', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', name='uq_student_profiles_user')
    )
    op.create_index(op.f('ix_student_profiles_id'), 'student_profiles', ['id'], unique=False)

    # 5. Create Schools table (UUID)
    op.create_table(
        'schools',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('city', sa.String(), nullable=True),
        sa.Column('arrondissement', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_schools_id'), 'schools', ['id'], unique=False)
    op.create_index('idx_schools_city', 'schools', ['city'], unique=False)

    # 6. Create Programs table (UUID)
    op.create_table(
        'programs',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('school_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('field_of_study', sa.String(), nullable=False),
        sa.Column('tuition', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('admission_requirements', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['school_id'], ['schools.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_programs_id'), 'programs', ['id'], unique=False)
    op.create_index('idx_programs_school_id', 'programs', ['school_id'], unique=False)
    op.create_index('idx_programs_field_of_study', 'programs', ['field_of_study'], unique=False)

    # 7. Create Applications table (UUID)
    op.create_table(
        'applications',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('program_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(), server_default=sa.text("'submitted'"), nullable=False),
        sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['program_id'], ['programs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['student_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('student_id', 'program_id', name='uq_applications_student_program')
    )
    op.create_index(op.f('ix_applications_id'), 'applications', ['id'], unique=False)
    op.create_index('idx_applications_student_id', 'applications', ['student_id'], unique=False)
    op.create_index('idx_applications_program_id', 'applications', ['program_id'], unique=False)
    op.create_index('idx_applications_status', 'applications', ['status'], unique=False)

    # 8. Create Favorites table (UUID)
    op.create_table(
        'favorites',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('school_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['school_id'], ['schools.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['student_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('student_id', 'school_id', name='uq_favorites_student_school')
    )
    op.create_index(op.f('ix_favorites_id'), 'favorites', ['id'], unique=False)
    op.create_index('idx_favorites_student_id', 'favorites', ['student_id'], unique=False)
    op.create_index('idx_favorites_school_id', 'favorites', ['school_id'], unique=False)

    # 9. Create Documents table (UUID)
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('file_url', sa.String(), nullable=False),
        sa.Column('doc_type', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['student_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_id'), 'documents', ['id'], unique=False)
    op.create_index('idx_documents_student_id', 'documents', ['student_id'], unique=False)

    # 10. Enable Row Level Security
    op.execute("ALTER TABLE users ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE student_profiles ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE schools ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE programs ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE applications ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE favorites ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE documents ENABLE ROW LEVEL SECURITY;")

    # Neon compatibility shim: Supabase provides auth.uid() natively, Neon does not
    op.execute("CREATE SCHEMA IF NOT EXISTS auth;")
    op.execute("""
        CREATE OR REPLACE FUNCTION auth.uid()
        RETURNS uuid
        LANGUAGE sql
        STABLE
        AS $$
          SELECT NULLIF(current_setting('app.current_user_id', true), '')::uuid
        $$;
    """)

    # 11. Create current_student_id() helper function
    op.execute("""
        CREATE OR REPLACE FUNCTION current_student_id()
        RETURNS uuid
        LANGUAGE sql
        STABLE
        SECURITY DEFINER
        SET search_path = public
        AS $$
          SELECT id FROM student_profiles WHERE user_id = auth.uid()
        $$;
    """)

    # 12. Create RLS Policies
    # Users policies
    op.execute("""
        CREATE POLICY "Users can view own row"
          ON users FOR SELECT
          USING (auth.uid() = id);
    """)
    op.execute("""
        CREATE POLICY "Users can update own row"
          ON users FOR UPDATE
          USING (auth.uid() = id)
          WITH CHECK (auth.uid() = id);
    """)

    # Student profiles policies
    op.execute("""
        CREATE POLICY "Students can view own profile"
          ON student_profiles FOR SELECT
          USING (auth.uid() = user_id);
    """)
    op.execute("""
        CREATE POLICY "Students can create own profile"
          ON student_profiles FOR INSERT
          WITH CHECK (auth.uid() = user_id);
    """)
    op.execute("""
        CREATE POLICY "Students can update own profile"
          ON student_profiles FOR UPDATE
          USING (auth.uid() = user_id)
          WITH CHECK (auth.uid() = user_id);
    """)

    # Schools & Programs policies (no Supabase "authenticated" role on Neon; app enforces auth)
    op.execute("""
        CREATE POLICY "Any authenticated user can view schools"
          ON schools FOR SELECT
          USING (true);
    """)
    op.execute("""
        CREATE POLICY "Any authenticated user can view programs"
          ON programs FOR SELECT
          USING (true);
    """)

    # Applications policies
    op.execute("""
        CREATE POLICY "Students can view own applications"
          ON applications FOR SELECT
          USING (student_id = current_student_id());
    """)
    op.execute("""
        CREATE POLICY "Students can create own applications"
          ON applications FOR INSERT
          WITH CHECK (student_id = current_student_id());
    """)
    op.execute("""
        CREATE POLICY "Students can update own applications"
          ON applications FOR UPDATE
          USING (student_id = current_student_id())
          WITH CHECK (student_id = current_student_id());
    """)

    # Favorites policies
    op.execute("""
        CREATE POLICY "Students can view own favorites"
          ON favorites FOR SELECT
          USING (student_id = current_student_id());
    """)
    op.execute("""
        CREATE POLICY "Students can add own favorites"
          ON favorites FOR INSERT
          WITH CHECK (student_id = current_student_id());
    """)
    op.execute("""
        CREATE POLICY "Students can remove own favorites"
          ON favorites FOR DELETE
          USING (student_id = current_student_id());
    """)

    # Documents policies
    op.execute("""
        CREATE POLICY "Students can view own documents"
          ON documents FOR SELECT
          USING (student_id = current_student_id());
    """)
    op.execute("""
        CREATE POLICY "Students can upload own documents"
          ON documents FOR INSERT
          WITH CHECK (student_id = current_student_id());
    """)
    op.execute("""
        CREATE POLICY "Students can delete own documents"
          ON documents FOR DELETE
          USING (student_id = current_student_id());
    """)


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS current_student_id() CASCADE;")
    op.execute("DROP FUNCTION IF EXISTS auth.uid() CASCADE;")
    op.execute("DROP TABLE IF EXISTS favorites CASCADE;")
    op.execute("DROP TABLE IF EXISTS documents CASCADE;")
    op.execute("DROP TABLE IF EXISTS applications CASCADE;")
    op.execute("DROP TABLE IF EXISTS student_profiles CASCADE;")
    op.execute("DROP TABLE IF EXISTS programs CASCADE;")
    op.execute("DROP TABLE IF EXISTS schools CASCADE;")
    op.execute("DROP TABLE IF EXISTS users CASCADE;")
