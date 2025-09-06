-- Event Popularity Report
-- Shows events ranked by total number of registrations

SELECT 
    e.event_id,
    e.title as event_name,
    e.event_type,
    c.name as college_name,
    c.code as college_code,
    e.start_datetime,
    e.end_datetime,
    e.max_capacity,
    e.location,
    COUNT(DISTINCT r.registration_id) as total_registrations,
    COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) as active_registrations,
    COUNT(DISTINCT CASE WHEN r.status = 'cancelled' THEN r.registration_id END) as cancelled_registrations,
    CASE 
        WHEN e.max_capacity IS NULL THEN 'Unlimited'
        WHEN e.max_capacity = 0 THEN '0%'
        ELSE ROUND((COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) * 100.0 / e.max_capacity), 2) || '%'
    END as capacity_utilization,
    CASE 
        WHEN COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) = 0 THEN 'No Registrations'
        WHEN COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) >= COALESCE(e.max_capacity, 999999) THEN 'Full'
        WHEN COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) >= COALESCE(e.max_capacity * 0.8, 999999) THEN 'Nearly Full'
        WHEN COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) >= COALESCE(e.max_capacity * 0.5, 999999) THEN 'Half Full'
        ELSE 'Available'
    END as registration_status
FROM events e
LEFT JOIN colleges c ON e.college_id = c.college_id
LEFT JOIN registrations r ON e.event_id = r.event_id
WHERE e.status = 'active'
GROUP BY e.event_id, e.title, e.event_type, c.name, c.code, 
         e.start_datetime, e.end_datetime, e.max_capacity, e.location
ORDER BY total_registrations DESC, e.start_datetime ASC;
