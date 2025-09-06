-- Bonus Reports and Advanced Analytics
-- Additional insights and special queries

-- 1. TOP 3 MOST ACTIVE STUDENTS
-- Students with highest participation across all metrics
SELECT 
    s.student_id,
    s.name as student_name,
    s.email,
    c.name as college_name,
    s.year_of_study,
    s.department,
    COUNT(DISTINCT r.registration_id) as total_registrations,
    COUNT(DISTINCT a.attendance_id) as events_attended,
    COUNT(DISTINCT CASE WHEN a.feedback_rating IS NOT NULL THEN a.attendance_id END) as feedback_provided,
    ROUND(AVG(a.feedback_rating), 2) as avg_feedback_given,
    -- Activity score calculation
    (COUNT(DISTINCT r.registration_id) * 1.0 + 
     COUNT(DISTINCT a.attendance_id) * 2.0 + 
     COUNT(DISTINCT CASE WHEN a.feedback_rating IS NOT NULL THEN a.attendance_id END) * 1.5) as activity_score,
    STRING_AGG(DISTINCT e.event_type, ', ' ORDER BY e.event_type) as event_types_participated
FROM students s
LEFT JOIN colleges c ON s.college_id = c.college_id
LEFT JOIN registrations r ON s.student_id = r.student_id AND r.status = 'registered'
LEFT JOIN attendance a ON r.registration_id = a.registration_id
LEFT JOIN events e ON r.event_id = e.event_id
WHERE s.is_active = TRUE
GROUP BY s.student_id, s.name, s.email, c.name, s.year_of_study, s.department
HAVING COUNT(DISTINCT r.registration_id) > 0
ORDER BY activity_score DESC, events_attended DESC, feedback_provided DESC
LIMIT 3;

-- 2. EVENTS WITH HIGHEST AND LOWEST FEEDBACK RATINGS
-- Top 5 highest and lowest rated events with detailed breakdown
(
    SELECT 
        'HIGHEST RATED' as ranking_type,
        ROW_NUMBER() OVER (ORDER BY AVG(a.feedback_rating) DESC, COUNT(a.feedback_rating) DESC) as rank,
        e.title as event_name,
        e.event_type,
        c.name as college_name,
        ROUND(AVG(a.feedback_rating), 2) as avg_rating,
        COUNT(a.feedback_rating) as feedback_count,
        ROUND((COUNT(CASE WHEN a.feedback_rating >= 4 THEN 1 END) * 100.0 / COUNT(a.feedback_rating)), 1) as positive_percentage,
        e.start_datetime
    FROM events e
    LEFT JOIN colleges c ON e.college_id = c.college_id
    LEFT JOIN registrations r ON e.event_id = r.event_id
    LEFT JOIN attendance a ON r.registration_id = a.registration_id
    WHERE e.status = 'active' AND a.feedback_rating IS NOT NULL
    GROUP BY e.event_id, e.title, e.event_type, c.name, e.start_datetime
    HAVING COUNT(a.feedback_rating) >= 3
    ORDER BY avg_rating DESC, feedback_count DESC
    LIMIT 5
)
UNION ALL
(
    SELECT 
        'LOWEST RATED' as ranking_type,
        ROW_NUMBER() OVER (ORDER BY AVG(a.feedback_rating) ASC, COUNT(a.feedback_rating) DESC) as rank,
        e.title as event_name,
        e.event_type,
        c.name as college_name,
        ROUND(AVG(a.feedback_rating), 2) as avg_rating,
        COUNT(a.feedback_rating) as feedback_count,
        ROUND((COUNT(CASE WHEN a.feedback_rating >= 4 THEN 1 END) * 100.0 / COUNT(a.feedback_rating)), 1) as positive_percentage,
        e.start_datetime
    FROM events e
    LEFT JOIN colleges c ON e.college_id = c.college_id
    LEFT JOIN registrations r ON e.event_id = r.event_id
    LEFT JOIN attendance a ON r.registration_id = a.registration_id
    WHERE e.status = 'active' AND a.feedback_rating IS NOT NULL
    GROUP BY e.event_id, e.title, e.event_type, c.name, e.start_datetime
    HAVING COUNT(a.feedback_rating) >= 3
    ORDER BY avg_rating ASC, feedback_count DESC
    LIMIT 5
)
ORDER BY ranking_type DESC, rank ASC;

-- 3. FLEXIBLE REPORTS WITH FILTERS
-- Create parameterized views for different filter combinations

-- A. Events by Type and College Filter
CREATE OR REPLACE VIEW events_by_filters AS
SELECT 
    e.event_id,
    e.title,
    e.event_type,
    c.name as college_name,
    c.code as college_code,
    e.start_datetime,
    e.end_datetime,
    e.location,
    e.max_capacity,
    COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) as registrations,
    COUNT(DISTINCT a.attendance_id) as attendance,
    ROUND(AVG(a.feedback_rating), 2) as avg_rating,
    CASE 
        WHEN COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) = 0 THEN 0
        ELSE ROUND((COUNT(DISTINCT a.attendance_id) * 100.0 / COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END)), 2)
    END as attendance_percentage
FROM events e
LEFT JOIN colleges c ON e.college_id = c.college_id
LEFT JOIN registrations r ON e.event_id = r.event_id
LEFT JOIN attendance a ON r.registration_id = a.registration_id
WHERE e.status = 'active'
GROUP BY e.event_id, e.title, e.event_type, c.name, c.code, e.start_datetime, e.end_datetime, e.location, e.max_capacity;

-- B. Filter by Workshop events
SELECT * FROM events_by_filters 
WHERE event_type = 'workshop'
ORDER BY avg_rating DESC, attendance_percentage DESC;

-- C. Filter by specific college (example: MIT)
SELECT * FROM events_by_filters 
WHERE college_code = 'MIT'
ORDER BY start_datetime DESC;

-- D. Filter by date range (last 30 days from current date)
SELECT * FROM events_by_filters 
WHERE start_datetime >= CURRENT_DATE - INTERVAL '30 days'
  AND start_datetime <= CURRENT_DATE + INTERVAL '30 days'
ORDER BY start_datetime ASC;

-- 4. COLLEGE-WISE PARTICIPATION STATISTICS
-- Comprehensive college comparison with advanced metrics
SELECT 
    c.college_id,
    c.name as college_name,
    c.code as college_code,
    c.city,
    c.state,
    -- Event statistics
    COUNT(DISTINCT e.event_id) as total_events_hosted,
    COUNT(DISTINCT CASE WHEN e.start_datetime > CURRENT_DATE THEN e.event_id END) as upcoming_events,
    COUNT(DISTINCT CASE WHEN e.start_datetime < CURRENT_DATE THEN e.event_id END) as completed_events,
    -- Student statistics
    COUNT(DISTINCT s.student_id) as total_students,
    COUNT(DISTINCT r.student_id) as active_students,
    ROUND((COUNT(DISTINCT r.student_id) * 100.0 / NULLIF(COUNT(DISTINCT s.student_id), 0)), 2) as student_participation_rate,
    -- Registration and attendance statistics
    COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) as total_registrations,
    COUNT(DISTINCT a.attendance_id) as total_attendance,
    ROUND((COUNT(DISTINCT a.attendance_id) * 100.0 / NULLIF(COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END), 0)), 2) as attendance_rate,
    -- Feedback statistics
    COUNT(DISTINCT CASE WHEN a.feedback_rating IS NOT NULL THEN a.attendance_id END) as feedback_responses,
    ROUND(AVG(a.feedback_rating), 2) as avg_feedback_rating,
    ROUND((COUNT(DISTINCT CASE WHEN a.feedback_rating IS NOT NULL THEN a.attendance_id END) * 100.0 / NULLIF(COUNT(DISTINCT a.attendance_id), 0)), 2) as feedback_response_rate,
    -- Event type diversity
    COUNT(DISTINCT e.event_type) as event_type_diversity,
    -- Capacity utilization
    ROUND(AVG(
        CASE 
            WHEN e.max_capacity IS NULL THEN 100
            ELSE (COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) * 100.0 / e.max_capacity)
        END
    ), 2) as avg_capacity_utilization,
    -- Performance ranking
    RANK() OVER (ORDER BY AVG(a.feedback_rating) DESC, COUNT(DISTINCT a.attendance_id) DESC) as performance_rank
FROM colleges c
LEFT JOIN students s ON c.college_id = s.college_id AND s.is_active = TRUE
LEFT JOIN events e ON c.college_id = e.college_id AND e.status = 'active'
LEFT JOIN registrations r ON e.event_id = r.event_id
LEFT JOIN attendance a ON r.registration_id = a.registration_id
GROUP BY c.college_id, c.name, c.code, c.city, c.state
ORDER BY performance_rank ASC, total_events_hosted DESC;

-- 5. EVENT SUCCESS METRICS DASHBOARD
-- Comprehensive success metrics for each event
SELECT 
    e.event_id,
    e.title as event_name,
    e.event_type,
    c.name as college_name,
    e.start_datetime,
    -- Basic metrics
    e.max_capacity,
    COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) as registrations,
    COUNT(DISTINCT a.attendance_id) as attendance,
    COUNT(DISTINCT CASE WHEN a.feedback_rating IS NOT NULL THEN a.attendance_id END) as feedback_count,
    -- Calculated percentages
    CASE 
        WHEN e.max_capacity IS NULL THEN 'N/A'
        ELSE ROUND((COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) * 100.0 / e.max_capacity), 1) || '%'
    END as capacity_utilization,
    CASE 
        WHEN COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) = 0 THEN 0
        ELSE ROUND((COUNT(DISTINCT a.attendance_id) * 100.0 / COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END)), 1)
    END as attendance_rate,
    CASE 
        WHEN COUNT(DISTINCT a.attendance_id) = 0 THEN 0
        ELSE ROUND((COUNT(DISTINCT CASE WHEN a.feedback_rating IS NOT NULL THEN a.attendance_id END) * 100.0 / COUNT(DISTINCT a.attendance_id)), 1)
    END as feedback_rate,
    -- Quality metrics
    ROUND(AVG(a.feedback_rating), 2) as avg_rating,
    COUNT(CASE WHEN a.feedback_rating >= 4 THEN 1 END) as positive_feedback,
    COUNT(CASE WHEN a.feedback_rating <= 2 THEN 1 END) as negative_feedback,
    -- Success score calculation (weighted average of metrics)
    CASE 
        WHEN COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) = 0 THEN 0
        ELSE ROUND(
            (LEAST(COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) * 100.0 / COALESCE(e.max_capacity, COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END)), 100) * 0.3 +
             COUNT(DISTINCT a.attendance_id) * 100.0 / COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) * 0.4 +
             COALESCE(AVG(a.feedback_rating), 0) * 20 * 0.3), 2
        )
    END as success_score,
    -- Success category
    CASE 
        WHEN COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) = 0 THEN 'No Data'
        WHEN ROUND(
            (LEAST(COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) * 100.0 / COALESCE(e.max_capacity, COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END)), 100) * 0.3 +
             COUNT(DISTINCT a.attendance_id) * 100.0 / COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) * 0.4 +
             COALESCE(AVG(a.feedback_rating), 0) * 20 * 0.3), 2
        ) >= 80 THEN 'Highly Successful'
        WHEN ROUND(
            (LEAST(COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) * 100.0 / COALESCE(e.max_capacity, COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END)), 100) * 0.3 +
             COUNT(DISTINCT a.attendance_id) * 100.0 / COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) * 0.4 +
             COALESCE(AVG(a.feedback_rating), 0) * 20 * 0.3), 2
        ) >= 60 THEN 'Successful'
        WHEN ROUND(
            (LEAST(COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) * 100.0 / COALESCE(e.max_capacity, COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END)), 100) * 0.3 +
             COUNT(DISTINCT a.attendance_id) * 100.0 / COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) * 0.4 +
             COALESCE(AVG(a.feedback_rating), 0) * 20 * 0.3), 2
        ) >= 40 THEN 'Moderately Successful'
        ELSE 'Needs Improvement'
    END as success_category
FROM events e
LEFT JOIN colleges c ON e.college_id = c.college_id
LEFT JOIN registrations r ON e.event_id = r.event_id
LEFT JOIN attendance a ON r.registration_id = a.registration_id
WHERE e.status = 'active'
GROUP BY e.event_id, e.title, e.event_type, c.name, e.start_datetime, e.max_capacity
ORDER BY success_score DESC, avg_rating DESC;

-- 6. PREDICTIVE ANALYTICS - RISK FACTORS
-- Identify events that might have low attendance based on historical patterns
SELECT 
    e.event_id,
    e.title as event_name,
    e.event_type,
    c.name as college_name,
    e.start_datetime,
    e.max_capacity,
    COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) as current_registrations,
    -- Risk factors
    CASE 
        WHEN e.start_datetime - CURRENT_DATE < INTERVAL '7 days' AND COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) < COALESCE(e.max_capacity * 0.3, 10) THEN 'High Risk - Low Registration'
        WHEN EXTRACT(DOW FROM e.start_datetime) IN (0, 6) THEN 'Medium Risk - Weekend Event'
        WHEN EXTRACT(HOUR FROM e.start_datetime) < 9 OR EXTRACT(HOUR FROM e.start_datetime) > 17 THEN 'Medium Risk - Off Hours'
        WHEN COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) < COALESCE(e.max_capacity * 0.5, 15) THEN 'Medium Risk - Below Average Registration'
        ELSE 'Low Risk'
    END as risk_assessment,
    -- Recommendations
    CASE 
        WHEN COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) < COALESCE(e.max_capacity * 0.3, 10) THEN 'Increase marketing efforts'
        WHEN EXTRACT(DOW FROM e.start_datetime) IN (0, 6) THEN 'Consider rescheduling to weekday'
        WHEN EXTRACT(HOUR FROM e.start_datetime) < 9 THEN 'Consider later start time'
        WHEN EXTRACT(HOUR FROM e.start_datetime) > 17 THEN 'Consider earlier start time'
        ELSE 'Continue current strategy'
    END as recommendation
FROM events e
LEFT JOIN colleges c ON e.college_id = c.college_id
LEFT JOIN registrations r ON e.event_id = r.event_id
WHERE e.status = 'active' 
  AND e.start_datetime > CURRENT_DATE
GROUP BY e.event_id, e.title, e.event_type, c.name, e.start_datetime, e.max_capacity
ORDER BY 
    CASE 
        WHEN e.start_datetime - CURRENT_DATE < INTERVAL '7 days' AND COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) < COALESCE(e.max_capacity * 0.3, 10) THEN 1
        WHEN EXTRACT(DOW FROM e.start_datetime) IN (0, 6) THEN 2
        WHEN EXTRACT(HOUR FROM e.start_datetime) < 9 OR EXTRACT(HOUR FROM e.start_datetime) > 17 THEN 3
        ELSE 4
    END,
    e.start_datetime ASC;
