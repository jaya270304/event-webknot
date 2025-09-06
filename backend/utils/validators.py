"""
Data validation utilities for Campus Event Management Platform
Validates input data for all API endpoints with comprehensive error messages
"""

from datetime import datetime, timedelta
import re

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_event_data(data, is_update=False):
    """
    Validate event creation/update data
    Returns: {'valid': bool, 'message': str}
    """
    if not data:
        return {'valid': False, 'message': 'No data provided'}
    
    required_fields = ['title', 'event_type', 'start_datetime', 'end_datetime']
    if not is_update:
        required_fields.append('college_id')
    
    # Check required fields
    for field in required_fields:
        if field not in data or not data[field]:
            return {'valid': False, 'message': f'Missing required field: {field}'}
    
    # Validate event type
    valid_event_types = ['hackathon', 'workshop', 'tech_talk', 'fest']
    if data.get('event_type') not in valid_event_types:
        return {'valid': False, 'message': f'Invalid event type. Must be one of: {", ".join(valid_event_types)}'}
    
    # Validate title length
    if len(data.get('title', '')) > 200:
        return {'valid': False, 'message': 'Title must be 200 characters or less'}
    
    # Validate datetime format and logic
    try:
        start_datetime = datetime.fromisoformat(data['start_datetime'].replace('Z', '+00:00'))
        end_datetime = datetime.fromisoformat(data['end_datetime'].replace('Z', '+00:00'))
        
        if end_datetime <= start_datetime:
            return {'valid': False, 'message': 'End datetime must be after start datetime'}
        
        # Check if event is not too far in the past (allow 1 hour grace period)
        if start_datetime < datetime.now().replace(tzinfo=start_datetime.tzinfo) - timedelta(hours=1):
            return {'valid': False, 'message': 'Event start time cannot be in the past'}
            
    except ValueError:
        return {'valid': False, 'message': 'Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}
    
    # Validate registration deadline if provided
    if data.get('registration_deadline'):
        try:
            reg_deadline = datetime.fromisoformat(data['registration_deadline'].replace('Z', '+00:00'))
            if reg_deadline > start_datetime:
                return {'valid': False, 'message': 'Registration deadline must be before event start time'}
        except ValueError:
            return {'valid': False, 'message': 'Invalid registration deadline format'}
    
    # Validate capacity
    if data.get('max_capacity') is not None:
        try:
            capacity = int(data['max_capacity'])
            if capacity <= 0:
                return {'valid': False, 'message': 'Maximum capacity must be a positive number'}
            if capacity > 10000:
                return {'valid': False, 'message': 'Maximum capacity seems unreasonably high (>10,000)'}
        except (ValueError, TypeError):
            return {'valid': False, 'message': 'Maximum capacity must be a valid number'}
    
    # Validate location length
    if data.get('location') and len(data['location']) > 300:
        return {'valid': False, 'message': 'Location must be 300 characters or less'}
    
    # Validate description length
    if data.get('description') and len(data['description']) > 2000:
        return {'valid': False, 'message': 'Description must be 2000 characters or less'}
    
    return {'valid': True, 'message': 'Valid event data'}

def validate_student_data(data):
    """
    Validate student creation data
    Returns: {'valid': bool, 'message': str}
    """
    if not data:
        return {'valid': False, 'message': 'No data provided'}
    
    required_fields = ['college_id', 'email', 'name', 'student_number']
    
    # Check required fields
    for field in required_fields:
        if field not in data or not data[field]:
            return {'valid': False, 'message': f'Missing required field: {field}'}
    
    # Validate email
    if not validate_email(data['email']):
        return {'valid': False, 'message': 'Invalid email format'}
    
    # Validate name length
    if len(data.get('name', '')) > 200:
        return {'valid': False, 'message': 'Name must be 200 characters or less'}
    
    if len(data.get('name', '')) < 2:
        return {'valid': False, 'message': 'Name must be at least 2 characters long'}
    
    # Validate student number
    if len(data.get('student_number', '')) > 50:
        return {'valid': False, 'message': 'Student number must be 50 characters or less'}
    
    # Validate year of study if provided
    if data.get('year_of_study') is not None:
        try:
            year = int(data['year_of_study'])
            if year < 1 or year > 4:
                return {'valid': False, 'message': 'Year of study must be between 1 and 4'}
        except (ValueError, TypeError):
            return {'valid': False, 'message': 'Year of study must be a valid number'}
    
    # Validate phone if provided
    if data.get('phone'):
        # Allow various phone formats
        phone_pattern = r'^[\+]?[1-9][\d]{0,15}$'
        clean_phone = re.sub(r'[\s\-\(\)]', '', data['phone'])
        if not re.match(phone_pattern, clean_phone):
            return {'valid': False, 'message': 'Invalid phone number format'}
    
    # Validate department length
    if data.get('department') and len(data['department']) > 100:
        return {'valid': False, 'message': 'Department must be 100 characters or less'}
    
    return {'valid': True, 'message': 'Valid student data'}

def validate_registration_data(data):
    """
    Validate event registration data
    Returns: {'valid': bool, 'message': str}
    """
    if not data:
        return {'valid': False, 'message': 'No data provided'}
    
    required_fields = ['event_id', 'student_id']
    
    # Check required fields
    for field in required_fields:
        if field not in data or not data[field]:
            return {'valid': False, 'message': f'Missing required field: {field}'}
    
    # Validate UUID format (basic check)
    import uuid
    try:
        uuid.UUID(str(data['event_id']))
        uuid.UUID(str(data['student_id']))
    except ValueError:
        return {'valid': False, 'message': 'Invalid ID format'}
    
    return {'valid': True, 'message': 'Valid registration data'}

def validate_feedback_data(data):
    """
    Validate feedback submission data
    Returns: {'valid': bool, 'message': str}
    """
    if not data:
        return {'valid': False, 'message': 'No data provided'}
    
    required_fields = ['attendance_id', 'rating']
    
    # Check required fields
    for field in required_fields:
        if field not in data or data[field] is None:
            return {'valid': False, 'message': f'Missing required field: {field}'}
    
    # Validate attendance_id format
    import uuid
    try:
        uuid.UUID(str(data['attendance_id']))
    except ValueError:
        return {'valid': False, 'message': 'Invalid attendance ID format'}
    
    # Validate rating
    try:
        rating = int(data['rating'])
        if rating < 1 or rating > 5:
            return {'valid': False, 'message': 'Rating must be between 1 and 5'}
    except (ValueError, TypeError):
        return {'valid': False, 'message': 'Rating must be a valid number between 1 and 5'}
    
    # Validate comment length if provided
    if data.get('comment') and len(data['comment']) > 1000:
        return {'valid': False, 'message': 'Comment must be 1000 characters or less'}
    
    # Check for inappropriate content (basic)
    if data.get('comment'):
        inappropriate_words = ['spam', 'hate', 'abuse']  # Simplified list
        comment_lower = data['comment'].lower()
        for word in inappropriate_words:
            if word in comment_lower:
                return {'valid': False, 'message': 'Comment contains inappropriate content'}
    
    return {'valid': True, 'message': 'Valid feedback data'}

def validate_attendance_data(data):
    """
    Validate attendance marking data
    Returns: {'valid': bool, 'message': str}
    """
    if not data:
        return {'valid': False, 'message': 'No data provided'}
    
    if 'registration_id' not in data or not data['registration_id']:
        return {'valid': False, 'message': 'Missing required field: registration_id'}
    
    # Validate registration_id format
    import uuid
    try:
        uuid.UUID(str(data['registration_id']))
    except ValueError:
        return {'valid': False, 'message': 'Invalid registration ID format'}
    
    # Validate check-in method if provided
    valid_methods = ['manual', 'qr_code', 'rfid']
    if data.get('check_in_method') and data['check_in_method'] not in valid_methods:
        return {'valid': False, 'message': f'Invalid check-in method. Must be one of: {", ".join(valid_methods)}'}
    
    return {'valid': True, 'message': 'Valid attendance data'}

def validate_college_data(data):
    """
    Validate college creation data
    Returns: {'valid': bool, 'message': str}
    """
    if not data:
        return {'valid': False, 'message': 'No data provided'}
    
    required_fields = ['name', 'code']
    
    # Check required fields
    for field in required_fields:
        if field not in data or not data[field]:
            return {'valid': False, 'message': f'Missing required field: {field}'}
    
    # Validate name length
    if len(data.get('name', '')) > 200:
        return {'valid': False, 'message': 'College name must be 200 characters or less'}
    
    if len(data.get('name', '')) < 2:
        return {'valid': False, 'message': 'College name must be at least 2 characters long'}
    
    # Validate code
    code = data.get('code', '').upper()
    if len(code) > 10:
        return {'valid': False, 'message': 'College code must be 10 characters or less'}
    
    if len(code) < 2:
        return {'valid': False, 'message': 'College code must be at least 2 characters long'}
    
    # Code should be alphanumeric
    if not re.match(r'^[A-Z0-9]+$', code):
        return {'valid': False, 'message': 'College code must contain only letters and numbers'}
    
    # Validate optional fields
    if data.get('contact_email') and not validate_email(data['contact_email']):
        return {'valid': False, 'message': 'Invalid contact email format'}
    
    if data.get('phone'):
        phone_pattern = r'^[\+]?[1-9][\d]{0,15}$'
        clean_phone = re.sub(r'[\s\-\(\)]', '', data['phone'])
        if not re.match(phone_pattern, clean_phone):
            return {'valid': False, 'message': 'Invalid phone number format'}
    
    return {'valid': True, 'message': 'Valid college data'}

def sanitize_input(data):
    """
    Sanitize input data to prevent XSS and other injection attacks
    Returns sanitized data
    """
    if isinstance(data, str):
        # Basic HTML tag removal
        data = re.sub(r'<[^>]+>', '', data)
        # Remove potentially dangerous characters
        data = re.sub(r'[<>"\']', '', data)
        return data.strip()
    elif isinstance(data, dict):
        return {key: sanitize_input(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    else:
        return data
