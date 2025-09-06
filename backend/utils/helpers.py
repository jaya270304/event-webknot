"""
Helper utilities for Campus Event Management Platform
Common functions used across the backend application
"""

from datetime import datetime, timezone
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'database'))

from connection import execute_query

def format_datetime(dt_string, format_type='iso'):
    """
    Format datetime string for various outputs
    Args:
        dt_string: datetime string or datetime object
        format_type: 'iso', 'readable', 'date_only', 'time_only'
    Returns:
        Formatted datetime string
    """
    if isinstance(dt_string, str):
        try:
            dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        except ValueError:
            return dt_string  # Return original if parsing fails
    elif isinstance(dt_string, datetime):
        dt = dt_string
    else:
        return str(dt_string)
    
    if format_type == 'iso':
        return dt.isoformat()
    elif format_type == 'readable':
        return dt.strftime('%B %d, %Y at %I:%M %p')
    elif format_type == 'date_only':
        return dt.strftime('%Y-%m-%d')
    elif format_type == 'time_only':
        return dt.strftime('%H:%M')
    else:
        return dt.isoformat()

def calculate_attendance_percentage(attended, registered):
    """
    Calculate attendance percentage with proper handling of edge cases
    Args:
        attended: number of attendees
        registered: number of registered students
    Returns:
        Attendance percentage as float (rounded to 2 decimal places)
    """
    if not registered or registered == 0:
        return 0.0
    
    percentage = (attended / registered) * 100
    return round(percentage, 2)

def get_event_stats(event_id):
    """
    Get comprehensive statistics for a specific event
    Args:
        event_id: UUID of the event
    Returns:
        Dictionary with event statistics
    """
    query = """
        SELECT 
            e.event_id,
            e.title,
            e.event_type,
            e.start_datetime,
            e.end_datetime,
            e.max_capacity,
            c.name as college_name,
            COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) as total_registrations,
            COUNT(DISTINCT CASE WHEN r.status = 'cancelled' THEN r.registration_id END) as cancelled_registrations,
            COUNT(DISTINCT a.attendance_id) as total_attendance,
            COUNT(DISTINCT CASE WHEN a.feedback_rating IS NOT NULL THEN a.attendance_id END) as feedback_count,
            ROUND(AVG(a.feedback_rating), 2) as avg_rating,
            COUNT(CASE WHEN a.feedback_rating = 5 THEN 1 END) as rating_5_count,
            COUNT(CASE WHEN a.feedback_rating = 4 THEN 1 END) as rating_4_count,
            COUNT(CASE WHEN a.feedback_rating = 3 THEN 1 END) as rating_3_count,
            COUNT(CASE WHEN a.feedback_rating = 2 THEN 1 END) as rating_2_count,
            COUNT(CASE WHEN a.feedback_rating = 1 THEN 1 END) as rating_1_count
        FROM events e
        LEFT JOIN colleges c ON e.college_id = c.college_id
        LEFT JOIN registrations r ON e.event_id = r.event_id
        LEFT JOIN attendance a ON r.registration_id = a.registration_id
        WHERE e.event_id = %s
        GROUP BY e.event_id, e.title, e.event_type, e.start_datetime, e.end_datetime, e.max_capacity, c.name
    """
    
    try:
        result = execute_query(query, (event_id,), fetch='one')
        
        if not result:
            return None
        
        stats = dict(result)
        
        # Calculate additional metrics
        stats['attendance_percentage'] = calculate_attendance_percentage(
            stats['total_attendance'], 
            stats['total_registrations']
        )
        
        # Calculate capacity utilization
        if stats['max_capacity']:
            stats['capacity_utilization'] = round(
                (stats['total_registrations'] / stats['max_capacity']) * 100, 2
            )
        else:
            stats['capacity_utilization'] = None
        
        # Calculate feedback response rate
        if stats['total_attendance'] > 0:
            stats['feedback_response_rate'] = round(
                (stats['feedback_count'] / stats['total_attendance']) * 100, 2
            )
        else:
            stats['feedback_response_rate'] = 0.0
        
        # Determine event status
        now = datetime.now(timezone.utc)
        start_time = stats['start_datetime']
        end_time = stats['end_datetime']
        
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        if isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        if now < start_time:
            stats['event_status'] = 'upcoming'
        elif start_time <= now <= end_time:
            stats['event_status'] = 'ongoing'
        else:
            stats['event_status'] = 'completed'
        
        return stats
        
    except Exception as e:
        print(f"Error getting event stats: {e}")
        return None

def get_student_activity_summary(student_id):
    """
    Get activity summary for a specific student
    Args:
        student_id: UUID of the student
    Returns:
        Dictionary with student activity summary
    """
    query = """
        SELECT 
            s.student_id,
            s.name,
            s.email,
            c.name as college_name,
            s.year_of_study,
            s.department,
            COUNT(DISTINCT r.registration_id) as total_registrations,
            COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) as active_registrations,
            COUNT(DISTINCT a.attendance_id) as events_attended,
            COUNT(DISTINCT CASE WHEN a.feedback_rating IS NOT NULL THEN a.attendance_id END) as feedback_provided,
            ROUND(AVG(a.feedback_rating), 2) as avg_rating_given,
            STRING_AGG(DISTINCT e.event_type, ', ') as event_types_attended,
            MAX(r.registered_at) as last_registration,
            MAX(a.checked_in_at) as last_attendance
        FROM students s
        LEFT JOIN colleges c ON s.college_id = c.college_id
        LEFT JOIN registrations r ON s.student_id = r.student_id
        LEFT JOIN attendance a ON r.registration_id = a.registration_id
        LEFT JOIN events e ON r.event_id = e.event_id
        WHERE s.student_id = %s
        GROUP BY s.student_id, s.name, s.email, c.name, s.year_of_study, s.department
    """
    
    try:
        result = execute_query(query, (student_id,), fetch='one')
        
        if not result:
            return None
        
        summary = dict(result)
        
        # Calculate attendance rate
        if summary['active_registrations'] > 0:
            summary['attendance_rate'] = calculate_attendance_percentage(
                summary['events_attended'], 
                summary['active_registrations']
            )
        else:
            summary['attendance_rate'] = 0.0
        
        # Determine activity level
        events_attended = summary['events_attended'] or 0
        if events_attended >= 5:
            summary['activity_level'] = 'highly_active'
        elif events_attended >= 3:
            summary['activity_level'] = 'active'
        elif events_attended >= 1:
            summary['activity_level'] = 'moderately_active'
        else:
            summary['activity_level'] = 'inactive'
        
        return summary
        
    except Exception as e:
        print(f"Error getting student activity summary: {e}")
        return None

def get_college_performance_metrics(college_id):
    """
    Get performance metrics for a specific college
    Args:
        college_id: UUID of the college
    Returns:
        Dictionary with college performance metrics
    """
    query = """
        SELECT 
            c.college_id,
            c.name,
            c.code,
            COUNT(DISTINCT e.event_id) as total_events,
            COUNT(DISTINCT s.student_id) as total_students,
            COUNT(DISTINCT r.registration_id) as total_registrations,
            COUNT(DISTINCT a.attendance_id) as total_attendance,
            COUNT(DISTINCT CASE WHEN a.feedback_rating IS NOT NULL THEN a.attendance_id END) as feedback_responses,
            ROUND(AVG(a.feedback_rating), 2) as avg_feedback_rating,
            COUNT(DISTINCT CASE WHEN e.start_datetime > CURRENT_DATE THEN e.event_id END) as upcoming_events,
            COUNT(DISTINCT e.event_type) as event_type_diversity
        FROM colleges c
        LEFT JOIN events e ON c.college_id = e.college_id AND e.status = 'active'
        LEFT JOIN students s ON c.college_id = s.college_id AND s.is_active = TRUE
        LEFT JOIN registrations r ON e.event_id = r.event_id AND r.status = 'registered'
        LEFT JOIN attendance a ON r.registration_id = a.registration_id
        WHERE c.college_id = %s
        GROUP BY c.college_id, c.name, c.code
    """
    
    try:
        result = execute_query(query, (college_id,), fetch='one')
        
        if not result:
            return None
        
        metrics = dict(result)
        
        # Calculate additional metrics
        metrics['attendance_rate'] = calculate_attendance_percentage(
            metrics['total_attendance'], 
            metrics['total_registrations']
        )
        
        # Calculate student participation rate
        if metrics['total_students'] > 0:
            active_students = execute_query(
                "SELECT COUNT(DISTINCT r.student_id) FROM registrations r JOIN events e ON r.event_id = e.event_id WHERE e.college_id = %s AND r.status = 'registered'",
                (college_id,), fetch='one'
            )['count']
            
            metrics['student_participation_rate'] = round(
                (active_students / metrics['total_students']) * 100, 2
            )
        else:
            metrics['student_participation_rate'] = 0.0
        
        # Calculate feedback response rate
        if metrics['total_attendance'] > 0:
            metrics['feedback_response_rate'] = round(
                (metrics['feedback_responses'] / metrics['total_attendance']) * 100, 2
            )
        else:
            metrics['feedback_response_rate'] = 0.0
        
        return metrics
        
    except Exception as e:
        print(f"Error getting college performance metrics: {e}")
        return None

def generate_success_score(registrations, attendance, avg_rating, max_capacity=None):
    """
    Generate a composite success score for events
    Args:
        registrations: number of registrations
        attendance: number of attendees
        avg_rating: average feedback rating
        max_capacity: maximum event capacity (optional)
    Returns:
        Success score as float (0-100)
    """
    if registrations == 0:
        return 0.0
    
    # Component scores (0-100 each)
    attendance_score = calculate_attendance_percentage(attendance, registrations)
    
    # Capacity utilization score
    if max_capacity and max_capacity > 0:
        capacity_score = min((registrations / max_capacity) * 100, 100)
    else:
        capacity_score = min(registrations * 5, 100)  # Assume 20+ registrations = 100%
    
    # Rating score (convert 1-5 to 0-100)
    rating_score = ((avg_rating or 0) - 1) * 25 if avg_rating else 0
    
    # Weighted average
    success_score = (
        attendance_score * 0.4 +      # 40% weight on attendance
        capacity_score * 0.3 +        # 30% weight on registration/capacity
        rating_score * 0.3            # 30% weight on feedback rating
    )
    
    return round(success_score, 2)

def format_event_for_api(event_data):
    """
    Format event data for API response
    Args:
        event_data: Raw event data from database
    Returns:
        Formatted event data dictionary
    """
    if not event_data:
        return None
    
    formatted = dict(event_data)
    
    # Format datetime fields
    datetime_fields = ['start_datetime', 'end_datetime', 'registration_deadline', 'created_at', 'updated_at']
    for field in datetime_fields:
        if formatted.get(field):
            formatted[field] = format_datetime(formatted[field], 'iso')
    
    # Ensure numeric fields are properly typed
    numeric_fields = ['max_capacity', 'registration_count', 'attendance_count']
    for field in numeric_fields:
        if formatted.get(field) is not None:
            formatted[field] = int(formatted[field])
    
    # Ensure float fields are properly typed
    float_fields = ['avg_rating', 'attendance_percentage']
    for field in float_fields:
        if formatted.get(field) is not None:
            formatted[field] = float(formatted[field])
    
    return formatted

def validate_uuid(uuid_string):
    """
    Validate if a string is a valid UUID
    Args:
        uuid_string: String to validate
    Returns:
        Boolean indicating validity
    """
    import uuid
    try:
        uuid.UUID(str(uuid_string))
        return True
    except ValueError:
        return False

def paginate_results(results, page=1, per_page=20):
    """
    Paginate query results
    Args:
        results: List of results
        page: Page number (1-based)
        per_page: Results per page
    Returns:
        Dictionary with paginated results and metadata
    """
    total = len(results)
    start = (page - 1) * per_page
    end = start + per_page
    
    paginated_results = results[start:end]
    
    return {
        'data': paginated_results,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'has_next': end < total,
            'has_prev': page > 1
        }
    }

def get_system_health():
    """
    Get system health metrics
    Returns:
        Dictionary with system health information
    """
    try:
        # Test database connectivity
        result = execute_query("SELECT COUNT(*) as total FROM colleges", fetch='one')
        db_healthy = result is not None
        
        # Get basic system stats
        stats = execute_query("""
            SELECT 
                (SELECT COUNT(*) FROM colleges) as total_colleges,
                (SELECT COUNT(*) FROM events WHERE status = 'active') as active_events,
                (SELECT COUNT(*) FROM students WHERE is_active = TRUE) as active_students,
                (SELECT COUNT(*) FROM registrations WHERE status = 'registered') as active_registrations
        """, fetch='one')
        
        return {
            'status': 'healthy' if db_healthy else 'unhealthy',
            'database': 'connected' if db_healthy else 'disconnected',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'stats': dict(stats) if stats else {}
        }
        
    except Exception as e:
        return {
            'status': 'unhealthy',
            'database': 'disconnected',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'error': str(e),
            'stats': {}
        }
