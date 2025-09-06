-- Feedback Reports
-- Multiple queries for feedback analysis and ratings

-- 1. AVERAGE FEEDBACK SCORE PER EVENT
-- Shows average ratings and feedback statistics for each event
SELECT 
    e.event_id,
    e.title as event_name,
    e.event_type,
    c.name as college_name,
    e.start_datetime,
    COUNT(DISTINCT a.attendance_id) as total_attendees,
    COUNT(DISTINCT CASE WHEN a.feedback_rating IS NOT NULL THEN a.attendance_id END) as feedback_responses,
    ROUND((COUNT(DISTINCT CASE WHEN a.feedback_rating IS NOT NULL THEN a.attendance_id END) * 100.0 / 
           NULLIF(COUNT(DISTINCT a.attendance_id), 0)), 2) as feedback_response_rate,
    ROUND(AVG(a.feedback_rating), 2) as avg_rating,
    MIN(a.feedback_rating) as min_rating,
    MAX(a.feedback_rating) as max_rating,
    MODE() WITHIN GROUP (ORDER BY a.feedback_rating) as most_common_rating,
    -- Rating distribution
    COUNT(CASE WHEN a.feedback_rating = 5 THEN 1 END) as rating_5_count,
    COUNT(CASE WHEN a.feedback_rating = 4 THEN 1 END) as rating_4_count,
    COUNT(CASE WHEN a.feedback_rating = 3 THEN 1 END) as rating_3_count,
    COUNT(CASE WHEN a.feedback_rating = 2 THEN 1 END) as rating_2_count,
    COUNT(CASE WHEN a.feedback_rating = 1 THEN 1 END) as rating_1_count,
    -- Performance categories
    CASE 
        WHEN AVG(a.feedback_rating) >= 4.5 THEN 'Excellent'
        WHEN AVG(a.feedback_rating) >= 4.0 THEN 'Very Good'
        WHEN AVG(a.feedback_rating) >= 3.5 THEN 'Good'
        WHEN AVG(a.feedback_rating) >= 3.0 THEN 'Average'
        WHEN AVG(a.feedback_rating) >= 2.0 THEN 'Below Average'
        ELSE 'Poor'
    END as performance_category
FROM events e
LEFT JOIN colleges c ON e.college_id = c.college_id
LEFT JOIN registrations r ON e.event_id = r.event_id
LEFT JOIN attendance a ON r.registration_id = a.registration_id
WHERE e.status = 'active'
GROUP BY e.event_id, e.title, e.event_type, c.name, e.start_datetime
HAVING COUNT(DISTINCT a.attendance_id) > 0
ORDER BY avg_rating DESC, feedback_responses DESC;

-- 2. FEEDBACK BY EVENT TYPE
-- Compare feedback ratings across different event types
SELECT 
    e.event_type,
    COUNT(DISTINCT e.event_id) as events_count,
    COUNT(DISTINCT a.attendance_id) as total_attendees,
    COUNT(DISTINCT CASE WHEN a.feedback_rating IS NOT NULL THEN a.attendance_id END) as feedback_responses,
    ROUND((COUNT(DISTINCT CASE WHEN a.feedback_rating IS NOT NULL THEN a.attendance_id END) * 100.0 / 
           NULLIF(COUNT(DISTINCT a.attendance_id), 0)), 2) as feedback_response_rate,
    ROUND(AVG(a.feedback_rating), 2) as avg_rating,
    ROUND(STDDEV(a.feedback_rating), 2) as rating_stddev,
    -- Rating distribution
    ROUND((COUNT(CASE WHEN a.feedback_rating = 5 THEN 1 END) * 100.0 / 
           NULLIF(COUNT(CASE WHEN a.feedback_rating IS NOT NULL THEN 1 END), 0)), 1) as percent_5_star,
    ROUND((COUNT(CASE WHEN a.feedback_rating = 4 THEN 1 END) * 100.0 / 
           NULLIF(COUNT(CASE WHEN a.feedback_rating IS NOT NULL THEN 1 END), 0)), 1) as percent_4_star,
    ROUND((COUNT(CASE WHEN a.feedback_rating = 3 THEN 1 END) * 100.0 / 
           NULLIF(COUNT(CASE WHEN a.feedback_rating IS NOT NULL THEN 1 END), 0)), 1) as percent_3_star,
    ROUND((COUNT(CASE WHEN a.feedback_rating = 2 THEN 1 END) * 100.0 / 
           NULLIF(COUNT(CASE WHEN a.feedback_rating IS NOT NULL THEN 1 END), 0)), 1) as percent_2_star,
    ROUND((COUNT(CASE WHEN a.feedback_rating = 1 THEN 1 END) * 100.0 / 
           NULLIF(COUNT(CASE WHEN a.feedback_rating IS NOT NULL THEN 1 END), 0)), 1) as percent_1_star
FROM events e
LEFT JOIN registrations r ON e.event_id = r.event_id
LEFT JOIN attendance a ON r.registration_id = a.registration_id
WHERE e.status = 'active'
GROUP BY e.event_type
ORDER BY avg_rating DESC;

-- 3. FEEDBACK BY COLLEGE
-- Compare feedback ratings across colleges
SELECT 
    c.college_id,
    c.name as college_name,
    c.code as college_code,
    COUNT(DISTINCT e.event_id) as events_hosted,
    COUNT(DISTINCT a.attendance_id) as total_attendees,
    COUNT(DISTINCT CASE WHEN a.feedback_rating IS NOT NULL THEN a.attendance_id END) as feedback_responses,
    ROUND((COUNT(DISTINCT CASE WHEN a.feedback_rating IS NOT NULL THEN a.attendance_id END) * 100.0 / 
           NULLIF(COUNT(DISTINCT a.attendance_id), 0)), 2) as feedback_response_rate,
    ROUND(AVG(a.feedback_rating), 2) as avg_rating,
    COUNT(CASE WHEN a.feedback_rating >= 4 THEN 1 END) as positive_ratings,
    COUNT(CASE WHEN a.feedback_rating <= 2 THEN 1 END) as negative_ratings,
    ROUND((COUNT(CASE WHEN a.feedback_rating >= 4 THEN 1 END) * 100.0 / 
           NULLIF(COUNT(CASE WHEN a.feedback_rating IS NOT NULL THEN 1 END), 0)), 2) as positive_percentage
FROM colleges c
LEFT JOIN events e ON c.college_id = e.college_id AND e.status = 'active'
LEFT JOIN registrations r ON e.event_id = r.event_id
LEFT JOIN attendance a ON r.registration_id = a.registration_id
GROUP BY c.college_id, c.name, c.code
HAVING COUNT(DISTINCT a.attendance_id) > 0
ORDER BY avg_rating DESC, positive_percentage DESC;

-- 4. TOP AND BOTTOM RATED EVENTS
-- Shows best and worst performing events based on feedback
(
    SELECT 
        'TOP RATED' as category,
        e.title as event_name,
        e.event_type,
        c.name as college_name,
        ROUND(AVG(a.feedback_rating), 2) as avg_rating,
        COUNT(CASE WHEN a.feedback_rating IS NOT NULL THEN 1 END) as feedback_count,
        e.start_datetime
    FROM events e
    LEFT JOIN colleges c ON e.college_id = c.college_id
    LEFT JOIN registrations r ON e.event_id = r.event_id
    LEFT JOIN attendance a ON r.registration_id = a.registration_id
    WHERE e.status = 'active' AND a.feedback_rating IS NOT NULL
    GROUP BY e.event_id, e.title, e.event_type, c.name, e.start_datetime
    HAVING COUNT(CASE WHEN a.feedback_rating IS NOT NULL THEN 1 END) >= 3  -- Minimum 3 feedback responses
    ORDER BY avg_rating DESC, feedback_count DESC
    LIMIT 5
)
UNION ALL
(
    SELECT 
        'BOTTOM RATED' as category,
        e.title as event_name,
        e.event_type,
        c.name as college_name,
        ROUND(AVG(a.feedback_rating), 2) as avg_rating,
        COUNT(CASE WHEN a.feedback_rating IS NOT NULL THEN 1 END) as feedback_count,
        e.start_datetime
    FROM events e
    LEFT JOIN colleges c ON e.college_id = c.college_id
    LEFT JOIN registrations r ON e.event_id = r.event_id
    LEFT JOIN attendance a ON r.registration_id = a.registration_id
    WHERE e.status = 'active' AND a.feedback_rating IS NOT NULL
    GROUP BY e.event_id, e.title, e.event_type, c.name, e.start_datetime
    HAVING COUNT(CASE WHEN a.feedback_rating IS NOT NULL THEN 1 END) >= 3  -- Minimum 3 feedback responses
    ORDER BY avg_rating ASC, feedback_count DESC
    LIMIT 5
);

-- 5. FEEDBACK COMMENTS ANALYSIS
-- Shows sample feedback comments and sentiment analysis
SELECT 
    e.title as event_name,
    e.event_type,
    c.name as college_name,
    a.feedback_rating,
    a.feedback_comment,
    a.feedback_submitted_at,
    LENGTH(a.feedback_comment) as comment_length,
    CASE 
        WHEN a.feedback_rating >= 4 THEN 'Positive'
        WHEN a.feedback_rating = 3 THEN 'Neutral'
        ELSE 'Negative'
    END as sentiment,
    -- Identify helpful comments (longer, detailed feedback)
    CASE 
        WHEN LENGTH(COALESCE(a.feedback_comment, '')) > 100 THEN 'Detailed'
        WHEN LENGTH(COALESCE(a.feedback_comment, '')) > 50 THEN 'Moderate'
        WHEN LENGTH(COALESCE(a.feedback_comment, '')) > 0 THEN 'Brief'
        ELSE 'Rating Only'
    END as comment_detail_level
FROM events e
LEFT JOIN colleges c ON e.college_id = c.college_id
LEFT JOIN registrations r ON e.event_id = r.event_id
LEFT JOIN attendance a ON r.registration_id = a.registration_id
WHERE e.status = 'active' 
  AND a.feedback_rating IS NOT NULL
  AND a.feedback_comment IS NOT NULL 
  AND LENGTH(a.feedback_comment) > 10
ORDER BY a.feedback_submitted_at DESC, a.feedback_rating DESC
LIMIT 50;

-- 6. FEEDBACK TRENDS OVER TIME
-- Shows how feedback ratings change over time
SELECT 
    DATE_TRUNC('month', e.start_datetime) as event_month,
    COUNT(DISTINCT e.event_id) as events_count,
    COUNT(DISTINCT a.attendance_id) as total_attendees,
    COUNT(CASE WHEN a.feedback_rating IS NOT NULL THEN 1 END) as feedback_responses,
    ROUND(AVG(a.feedback_rating), 2) as avg_rating,
    ROUND((COUNT(CASE WHEN a.feedback_rating IS NOT NULL THEN 1 END) * 100.0 / 
           NULLIF(COUNT(DISTINCT a.attendance_id), 0)), 2) as response_rate,
    COUNT(CASE WHEN a.feedback_rating >= 4 THEN 1 END) as positive_ratings,
    ROUND((COUNT(CASE WHEN a.feedback_rating >= 4 THEN 1 END) * 100.0 / 
           NULLIF(COUNT(CASE WHEN a.feedback_rating IS NOT NULL THEN 1 END), 0)), 2) as positive_percentage
FROM events e
LEFT JOIN registrations r ON e.event_id = r.event_id
LEFT JOIN attendance a ON r.registration_id = a.registration_id
WHERE e.status = 'active'
GROUP BY DATE_TRUNC('month', e.start_datetime)
HAVING COUNT(DISTINCT e.event_id) > 0
ORDER BY event_month DESC;
