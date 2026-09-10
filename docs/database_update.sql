-- =====================================================================
-- ApplyCM Database Schema Update Script
-- =====================================================================
-- Run this script in PostgreSQL / Neon SQL Editor to update
-- student_profiles and add education tracking columns and fields.
-- =====================================================================

-- 1. Add is_completed, declared_state, and education fields to student_profiles
ALTER TABLE student_profiles
  ADD COLUMN IF NOT EXISTS is_completed BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS declared_state VARCHAR(100),
  ADD COLUMN IF NOT EXISTS secondary_school VARCHAR(255),
  ADD COLUMN IF NOT EXISTS advanced_level_slip_image TEXT,
  ADD COLUMN IF NOT EXISTS ordinary_level_slip_image TEXT;

-- 2. Optional: Create dedicated education table if structured normalization is preferred
CREATE TABLE IF NOT EXISTS education (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    secondary_school VARCHAR(255),
    advanced_level_slip_image TEXT,
    ordinary_level_slip_image TEXT,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT uq_education_student UNIQUE (student_id)
);

-- 3. Enable RLS on education table if created
ALTER TABLE education ENABLE ROW LEVEL SECURITY;

-- 4. RLS Policies for education table
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'education' AND policyname = 'Students can view own education'
    ) THEN
        CREATE POLICY "Students can view own education"
          ON education FOR SELECT
          USING (student_id = current_student_id());
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'education' AND policyname = 'Students can manage own education'
    ) THEN
        CREATE POLICY "Students can manage own education"
          ON education FOR ALL
          USING (student_id = current_student_id());
    END IF;
END $$;
