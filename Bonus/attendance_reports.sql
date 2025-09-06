-- Attendance Reports
-- Multiple queries for different attendance analytics

-- 1. ATTENDANCE PERCENTAGE PER EVENT
-- Shows attendance rate for each event
SELECT 
    e.event_id,
    e.title as event_name,
    e.event_type,
    c.name as college_name,
    e.start_datetime,
    e.end_datetime,
    COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) as total_registered,
    COUNT(DISTINCT a.attendance_id) as total_attended,
    CASE 
        WHEN COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) = 0 THEN 0
        ELSE ROUND((COUNT(DISTINCT a.attendance_id) * 100.0 / COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END)), 2)
    END as attendance_percentage,
    CASE 
        WHEN COUNT(DISTINCT a.attendance_id) * 100.0 / NULLIF(COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END), 0) >= 90 THEN 'Excellent'
        WHEN COUNT(DISTINCT a.attendance_id) * 100.0 / NULLIF(COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END), 0) >= 80 THEN 'Good'
        WHEN COUNT(DISTINCT a.attendance_id) * 100.0 / NULLIF(COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END), 0) >= 60 THEN 'Average'
        WHEN COUNT(DISTINCT a.attendance_id) * 100.0 / NULLIF(COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END), 0) >= 40 THEN 'Below Average'
        ELSE 'Poor'
    END as attendance_grade
FROM events e
LEFT JOIN colleges c ON e.college_id = c.college_id
LEFT JOIN registrations r ON e.event_id = r.event_id
LEFT JOIN attendance a ON r.registration_id = a.registration_id
WHERE e.status = 'active'
GROUP BY e.event_id, e.title, e.event_type, c.name, e.start_datetime, e.end_datetime
ORDER BY attendance_percentage DESC, total_registered DESC;

-- 2. ATTENDANCE BY EVENT TYPE
-- Shows attendance statistics grouped by event type
SELECT 
    e.event_type,
    COUNT(DISTINCT e.event_id) as total_events,
    COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) as total_registrations,
    COUNT(DISTINCT a.attendance_id) as total_attendance,
    ROUND(AVG(
        CASE 
            WHEN COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) = 0 THEN 0
            ELSE (COUNT(DISTINCT a.attendance_id) * 100.0 / COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END))
        END
    ), 2) as avg_attendance_percentage,
    MIN(
        CASE 
            WHEN COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) = 0 THEN 0
            ELSE ROUND((COUNT(DISTINCT a.attendance_id) * 100.0 / COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END)), 2)
        END
    ) as min_attendance_percentage,
    MAX(
        CASE 
            WHEN COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) = 0 THEN 0
            ELSE ROUND((COUNT(DISTINCT a.attendance_id) * 100.0 / COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END)), 2)
        END
    ) as max_attendance_percentage
FROM events e
LEFT JOIN registrations r ON e.event_id = r.event_id
LEFT JOIN attendance a ON r.registration_id = a.registration_id
WHERE e.status = 'active'
GROUP BY e.event_type
ORDER BY avg_attendance_percentage DESC;

-- 3. ATTENDANCE BY COLLEGE
-- Shows attendance statistics by college
SELECT 
    c.college_id,
    c.name as college_name,
    c.code as college_code,
    COUNT(DISTINCT e.event_id) as events_hosted,
    COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) as total_registrations,
    COUNT(DISTINCT a.attendance_id) as total_attendance,
    CASE 
        WHEN COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) = 0 THEN 0
        ELSE ROUND((COUNT(DISTINCT a.attendance_id) * 100.0 / COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END)), 2)
    END as overall_attendance_percentage,
    ROUND(AVG(e.max_capacity), 0) as avg_event_capacity
FROM colleges c
LEFT JOIN events e ON c.college_id = e.college_id AND e.status = 'active'
LEFT JOIN registrations r ON e.event_id = r.event_id
LEFT JOIN attendance a ON r.registration_id = a.registration_id
GROUP BY c.college_id, c.name, c.code
ORDER BY overall_attendance_percentage DESC, total_registrations DESC;

-- 4. DAILY ATTENDANCE TRENDS
-- Shows attendance patterns by day of week
SELECT 
    EXTRACT(DOW FROM e.start_datetime) as day_of_week,
    CASE EXTRACT(DOW FROM e.start_datetime)
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday' 
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END as day_name,
    COUNT(DISTINCT e.event_id) as events_count,
    COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) as total_registrations,
    COUNT(DISTINCT a.attendance_id) as total_attendance,
    CASE 
        WHEN COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) = 0 THEN 0
        ELSE ROUND((COUNT(DISTINCT a.attendance_id) * 100.0 / COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END)), 2)
    END as attendance_percentage
FROM events e
LEFT JOIN registrations r ON e.event_id = r.event_id
LEFT JOIN attendance a ON r.registration_id = a.registration_id
WHERE e.status = 'active'
GROUP BY EXTRACT(DOW FROM e.start_datetime)
ORDER BY day_of_week;

-- 5. CHECK-IN METHOD ANALYSIS
-- Shows distribution of check-in methods used
SELECT 
    a.check_in_method,
    COUNT(*) as usage_count,
    ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM attendance)), 2) as percentage,
    COUNT(DISTINCT e.event_id) as events_used,
    COUNT(DISTINCT c.college_id) as colleges_used
FROM attendance a
JOIN registrations r ON a.registration_id = r.registration_id
JOIN events e ON r.event_id = e.event_id
JOIN colleges c ON e.college_id = c.college_id
GROUP BY a.check_in_method
ORDER BY usage_count DESC;
