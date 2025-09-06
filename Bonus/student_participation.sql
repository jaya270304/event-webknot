-- Student Participation Report
-- Shows how many events each student has registered for and attended

SELECT 
    s.student_id,
    s.name as student_name,
    s.email,
    s.student_number,
    c.name as college_name,
    c.code as college_code,
    s.year_of_study,
    s.department,
    COUNT(DISTINCT r.registration_id) as total_registrations,
    COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) as active_registrations,
    COUNT(DISTINCT CASE WHEN r.status = 'cancelled' THEN r.registration_id END) as cancelled_registrations,
    COUNT(DISTINCT a.attendance_id) as events_attended,
    COUNT(DISTINCT CASE WHEN a.feedback_rating IS NOT NULL THEN a.attendance_id END) as feedback_provided,
    CASE 
        WHEN COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) = 0 THEN 0
        ELSE ROUND((COUNT(DISTINCT a.attendance_id) * 100.0 / COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END)), 2)
    END as attendance_percentage,
    ROUND(AVG(a.feedback_rating), 2) as avg_feedback_rating,
    CASE 
        WHEN COUNT(DISTINCT r.registration_id) = 0 THEN 'Inactive'
        WHEN COUNT(DISTINCT a.attendance_id) = 0 THEN 'Registered Only'
        WHEN COUNT(DISTINCT a.attendance_id) >= 5 THEN 'Highly Active'
        WHEN COUNT(DISTINCT a.attendance_id) >= 3 THEN 'Active'
        WHEN COUNT(DISTINCT a.attendance_id) >= 1 THEN 'Moderately Active'
        ELSE 'Low Activity'
    END as activity_level,
    -- Event types attended
    STRING_AGG(DISTINCT e.event_type, ', ' ORDER BY e.event_type) as event_types_attended,
    MAX(r.registered_at) as last_registration_date,
    MAX(a.checked_in_at) as last_attendance_date
FROM students s
LEFT JOIN colleges c ON s.college_id = c.college_id
LEFT JOIN registrations r ON s.student_id = r.student_id
LEFT JOIN attendance a ON r.registration_id = a.registration_id
LEFT JOIN events e ON r.event_id = e.event_id
WHERE s.is_active = TRUE
GROUP BY s.student_id, s.name, s.email, s.student_number, c.name, c.code, s.year_of_study, s.department
ORDER BY events_attended DESC, total_registrations DESC, s.name ASC;
