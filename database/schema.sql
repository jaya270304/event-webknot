-- Campus Event Management Platform Database Schema
-- Complete table creation script for PostgreSQL

-- Drop existing tables if they exist (for clean reinstall)
DROP TABLE IF EXISTS attendance CASCADE;
DROP TABLE IF EXISTS registrations CASCADE;
DROP TABLE IF EXISTS students CASCADE;
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS colleges CASCADE;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. COLLEGES TABLE
CREATE TABLE colleges (
    college_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL,
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(50),
    contact_email VARCHAR(255),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. EVENTS TABLE  
CREATE TABLE events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    college_id UUID REFERENCES colleges(college_id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    event_type VARCHAR(20) CHECK (event_type IN ('hackathon', 'workshop', 'tech_talk', 'fest')) NOT NULL,
    start_datetime TIMESTAMP NOT NULL,
    end_datetime TIMESTAMP NOT NULL,
    location VARCHAR(300),
    max_capacity INTEGER DEFAULT NULL,
    registration_deadline TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'completed', 'draft')),
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_datetime CHECK (end_datetime > start_datetime),
    CONSTRAINT positive_capacity CHECK (max_capacity > 0 OR max_capacity IS NULL)
);

-- 3. STUDENTS TABLE
CREATE TABLE students (
    student_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    college_id UUID REFERENCES colleges(college_id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    student_number VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    year_of_study INTEGER CHECK (year_of_study BETWEEN 1 AND 4),
    department VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique constraint: student number unique per college
    UNIQUE(college_id, student_number)
);

-- 4. REGISTRATIONS TABLE
CREATE TABLE registrations (
    registration_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID REFERENCES events(event_id) ON DELETE CASCADE,
    student_id UUID REFERENCES students(student_id) ON DELETE CASCADE,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'registered' CHECK (status IN ('registered', 'cancelled', 'waitlisted')),
    registration_source VARCHAR(50) DEFAULT 'web',
    cancelled_at TIMESTAMP,
    cancellation_reason TEXT,
    
    -- Unique constraint: prevent duplicate registrations
    UNIQUE(event_id, student_id)
);

-- 5. ATTENDANCE TABLE
CREATE TABLE attendance (
    attendance_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    registration_id UUID UNIQUE REFERENCES registrations(registration_id) ON DELETE CASCADE,
    checked_in_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    checked_out_at TIMESTAMP,
    check_in_method VARCHAR(20) DEFAULT 'manual' CHECK (check_in_method IN ('manual', 'qr_code', 'rfid')),
    feedback_rating INTEGER CHECK (feedback_rating BETWEEN 1 AND 5),
    feedback_comment TEXT,
    feedback_submitted_at TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_checkout CHECK (checked_out_at IS NULL OR checked_out_at > checked_in_at)
);

-- CREATE INDEXES FOR PERFORMANCE
CREATE INDEX idx_events_college_type ON events(college_id, event_type);
CREATE INDEX idx_events_datetime ON events(start_datetime, end_datetime);
CREATE INDEX idx_events_status ON events(status);
CREATE INDEX idx_registrations_event ON registrations(event_id);
CREATE INDEX idx_registrations_student ON registrations(student_id);
CREATE INDEX idx_registrations_status ON registrations(status);
CREATE INDEX idx_attendance_rating ON attendance(feedback_rating);
CREATE INDEX idx_students_college ON students(college_id);
CREATE INDEX idx_students_email ON students(email);

-- CREATE VIEWS FOR COMMON QUERIES
CREATE OR REPLACE VIEW event_summary AS
SELECT 
    e.event_id,
    e.title,
    e.event_type,
    e.start_datetime,
    e.end_datetime,
    c.name as college_name,
    c.code as college_code,
    e.max_capacity,
    e.status,
    COUNT(DISTINCT r.registration_id) as total_registrations,
    COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) as active_registrations,
    COUNT(DISTINCT a.attendance_id) as total_attendance,
    ROUND(AVG(a.feedback_rating), 2) as avg_rating
FROM events e
LEFT JOIN colleges c ON e.college_id = c.college_id
LEFT JOIN registrations r ON e.event_id = r.event_id
LEFT JOIN attendance a ON r.registration_id = a.registration_id
GROUP BY e.event_id, e.title, e.event_type, e.start_datetime, e.end_datetime, 
         c.name, c.code, e.max_capacity, e.status;

-- TRIGGER FUNCTION FOR UPDATED_AT
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- CREATE TRIGGERS
CREATE TRIGGER update_colleges_updated_at BEFORE UPDATE ON colleges
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_events_updated_at BEFORE UPDATE ON events
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_students_updated_at BEFORE UPDATE ON students
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- GRANT PERMISSIONS (adjust as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO campus_event_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO campus_event_user;

-- Print confirmation
DO $$
BEGIN
    RAISE NOTICE 'Campus Event Management Database Schema created successfully!';
    RAISE NOTICE 'Tables: colleges, events, students, registrations, attendance';
    RAISE NOTICE 'Views: event_summary';
    RAISE NOTICE 'Indexes and triggers created';
END $$;
