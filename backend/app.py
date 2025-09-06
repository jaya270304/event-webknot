"""
Campus Event Management Platform - Complete Backend API System
This is the main Flask backend application that provides comprehensive REST APIs for managing:
- College registration and information
- Event creation, management and analytics
- Student registration and authentication
- Event registration and attendance tracking
- Feedback collection and reporting
- Analytics and reporting functionality

The system supports up to 50 colleges with 500 students each and 20 events per semester.
Compatible with Python 3.7+ and uses PostgreSQL for data storage.
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sys
import os
import logging
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'database'))

from connection import get_db_connection, execute_query, test_connection
from utils.validators import validate_event_data, validate_student_data, validate_registration_data, validate_feedback_data
from utils.helpers import format_datetime, calculate_attendance_percentage, get_event_stats
from datetime import datetime, timedelta
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'), 
           static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'))
CORS(app)

# Configuration
app.config['SECRET_KEY'] = 'campus_events_secret_key_2025'
app.config['JSON_SORT_KEYS'] = False

# Initialize database connection on startup
def initialize():
    """Initialize database connection and schema"""
    try:
        if test_connection():
            print("✅ Database connection successful")
        else:
            print("❌ Database connection failed")
    except Exception as e:
        print(f"❌ Database initialization error: {e}")

# Call initialize on startup
initialize()

# HTML Routes for frontend pages
@app.route('/')
def index():
    """Homepage"""
    logger.info("Serving homepage")
    return render_template('index.html')

@app.route('/admin')
def admin():
    """Admin portal page"""
    logger.info("Serving admin portal")
    return render_template('admin.html')

@app.route('/student')
def student():
    """Student portal page"""
    logger.info("Serving student portal")
    return render_template('student.html')

@app.route('/reports')
def reports():
    """Reports page"""
    logger.info("Serving reports page")
    return render_template('reports.html')

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found', 'message': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        test_connection()
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'disconnected',
            'error': str(e)
        }), 503

# COLLEGE MANAGEMENT ENDPOINTS

@app.route('/api/colleges', methods=['POST'])
def create_college():
    """Create a new college"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('name') or not data.get('code'):
            return jsonify({'error': 'Missing required fields: name and code'}), 400
        
        # Validate data
        if len(data.get('code', '')) > 10:
            return jsonify({'error': 'College code must be 10 characters or less'}), 400
        
        query = """
            INSERT INTO colleges (name, code, address, city, state, contact_email, phone)
            VALUES (%(name)s, %(code)s, %(address)s, %(city)s, %(state)s, %(contact_email)s, %(phone)s)
            RETURNING college_id, name, code, address, city, state, contact_email, phone, created_at
        """
        
        college_data = {
            'name': data['name'],
            'code': data['code'].upper(),
            'address': data.get('address'),
            'city': data.get('city'),
            'state': data.get('state'),
            'contact_email': data.get('contact_email'),
            'phone': data.get('phone')
        }
        
        result = execute_query(query, college_data, fetch='one')
        
        if result:
            return jsonify(dict(result)), 201
        else:
            return jsonify({'error': 'Failed to create college'}), 500
            
    except Exception as e:
        if 'duplicate key value violates unique constraint' in str(e):
            return jsonify({'error': 'College code already exists'}), 409
        return jsonify({'error': str(e)}), 500

@app.route('/api/colleges', methods=['GET'])
def get_colleges():
    """Get all colleges"""
    try:
        query = """
            SELECT c.college_id, c.name, c.code, c.address, c.city, c.state, c.contact_email, c.phone, c.created_at,
                   COUNT(DISTINCT e.event_id) as total_events,
                   COUNT(DISTINCT s.student_id) as total_students
            FROM colleges c
            LEFT JOIN events e ON c.college_id = e.college_id AND e.status = 'active'
            LEFT JOIN students s ON c.college_id = s.college_id AND s.is_active = TRUE
            GROUP BY c.college_id, c.name, c.code, c.address, c.city, c.state, c.contact_email, c.phone, c.created_at
            ORDER BY c.name ASC
        """
        
        colleges = execute_query(query, fetch='all')
        return jsonify([dict(college) for college in colleges])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/colleges/<college_id>', methods=['GET'])
def get_college(college_id):
    """Get specific college details"""
    try:
        query = """
            SELECT c.*, 
                   COUNT(DISTINCT e.event_id) as total_events,
                   COUNT(DISTINCT s.student_id) as total_students,
                   COUNT(DISTINCT CASE WHEN e.start_datetime > CURRENT_DATE THEN e.event_id END) as upcoming_events
            FROM colleges c
            LEFT JOIN events e ON c.college_id = e.college_id AND e.status = 'active'
            LEFT JOIN students s ON c.college_id = s.college_id AND s.is_active = TRUE
            WHERE c.college_id = %s
            GROUP BY c.college_id
        """
        
        college = execute_query(query, (college_id,), fetch='one')
        
        if college:
            return jsonify(dict(college))
        else:
            return jsonify({'error': 'College not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/colleges/<college_id>/events', methods=['GET'])
def get_college_events(college_id):
    """Get all events for a specific college"""
    try:
        query = """
            SELECT e.*, c.name as college_name, c.code as college_code,
                   COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) as registration_count,
                   COUNT(DISTINCT a.attendance_id) as attendance_count,
                   ROUND(AVG(a.feedback_rating), 2) as avg_rating
            FROM events e
            LEFT JOIN colleges c ON e.college_id = c.college_id
            LEFT JOIN registrations r ON e.event_id = r.event_id
            LEFT JOIN attendance a ON r.registration_id = a.registration_id
            WHERE e.college_id = %s AND e.status = 'active'
            GROUP BY e.event_id, c.name, c.code
            ORDER BY e.start_datetime ASC
        """
        
        events = execute_query(query, (college_id,), fetch='all')
        return jsonify([dict(event) for event in events])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# EVENT MANAGEMENT ENDPOINTS

@app.route('/api/events', methods=['POST'])
def create_event():
    """Create a new event"""
    try:
        data = request.get_json()
        
        # Validate event data
        validation_result = validate_event_data(data)
        if not validation_result['valid']:
            return jsonify({'error': validation_result['message']}), 400
        
        query = """
            INSERT INTO events (college_id, title, description, event_type, start_datetime, 
                              end_datetime, location, max_capacity, registration_deadline, created_by)
            VALUES (%(college_id)s, %(title)s, %(description)s, %(event_type)s, %(start_datetime)s,
                   %(end_datetime)s, %(location)s, %(max_capacity)s, %(registration_deadline)s, %(created_by)s)
            RETURNING event_id, college_id, title, description, event_type, start_datetime, 
                     end_datetime, location, max_capacity, registration_deadline, status, created_by, created_at
        """
        
        event_data = {
            'college_id': data['college_id'],
            'title': data['title'],
            'description': data.get('description', ''),
            'event_type': data['event_type'],
            'start_datetime': data['start_datetime'],
            'end_datetime': data['end_datetime'],
            'location': data.get('location'),
            'max_capacity': data.get('max_capacity'),
            'registration_deadline': data.get('registration_deadline'),
            'created_by': data.get('created_by', 'System')
        }
        
        result = execute_query(query, event_data, fetch='one')
        
        if result:
            return jsonify(dict(result)), 201
        else:
            return jsonify({'error': 'Failed to create event'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get all events with optional filters"""
    try:
        # Get query parameters for filtering
        college_id = request.args.get('college_id')
        event_type = request.args.get('event_type')
        status = request.args.get('status', 'active')
        
        # Build dynamic query
        where_conditions = ["e.status = %(status)s"]
        params = {'status': status}
        
        if college_id:
            where_conditions.append("e.college_id = %(college_id)s")
            params['college_id'] = college_id
            
        if event_type:
            where_conditions.append("e.event_type = %(event_type)s")
            params['event_type'] = event_type
        
        where_clause = " AND ".join(where_conditions)
        
        query = f"""
            SELECT e.*, c.name as college_name, c.code as college_code,
                   COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) as registration_count,
                   COUNT(DISTINCT a.attendance_id) as attendance_count,
                   ROUND(AVG(a.feedback_rating), 2) as avg_rating
            FROM events e
            LEFT JOIN colleges c ON e.college_id = c.college_id
            LEFT JOIN registrations r ON e.event_id = r.event_id
            LEFT JOIN attendance a ON r.registration_id = a.registration_id
            WHERE {where_clause}
            GROUP BY e.event_id, c.name, c.code
            ORDER BY e.start_datetime ASC
        """
        
        events = execute_query(query, params, fetch='all')
        return jsonify([dict(event) for event in events])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/events/<event_id>', methods=['GET'])
def get_event(event_id):
    """Get specific event details"""
    try:
        query = """
            SELECT e.*, c.name as college_name, c.code as college_code,
                   COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) as registration_count,
                   COUNT(DISTINCT a.attendance_id) as attendance_count,
                   ROUND(AVG(a.feedback_rating), 2) as avg_rating,
                   COUNT(DISTINCT CASE WHEN a.feedback_rating IS NOT NULL THEN a.attendance_id END) as feedback_count
            FROM events e
            LEFT JOIN colleges c ON e.college_id = c.college_id
            LEFT JOIN registrations r ON e.event_id = r.event_id
            LEFT JOIN attendance a ON r.registration_id = a.registration_id
            WHERE e.event_id = %s
            GROUP BY e.event_id, c.name, c.code
        """
        
        event = execute_query(query, (event_id,), fetch='one')
        
        if event:
            event_dict = dict(event)
            # Calculate attendance percentage
            if event_dict['registration_count'] > 0:
                event_dict['attendance_percentage'] = round((event_dict['attendance_count'] / event_dict['registration_count']) * 100, 2)
            else:
                event_dict['attendance_percentage'] = 0
            
            return jsonify(event_dict)
        else:
            return jsonify({'error': 'Event not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/events/<event_id>', methods=['PUT'])
def update_event(event_id):
    """Update an event"""
    try:
        data = request.get_json()
        
        # Validate event data
        validation_result = validate_event_data(data, is_update=True)
        if not validation_result['valid']:
            return jsonify({'error': validation_result['message']}), 400
        
        # Check if event exists
        existing_event = execute_query("SELECT event_id FROM events WHERE event_id = %s", (event_id,), fetch='one')
        if not existing_event:
            return jsonify({'error': 'Event not found'}), 404
        
        # Build update query dynamically
        update_fields = []
        params = {'event_id': event_id}
        
        updatable_fields = ['title', 'description', 'event_type', 'start_datetime', 'end_datetime', 
                           'location', 'max_capacity', 'registration_deadline', 'status']
        
        for field in updatable_fields:
            if field in data:
                update_fields.append(f"{field} = %({field})s")
                params[field] = data[field]
        
        if not update_fields:
            return jsonify({'error': 'No fields to update'}), 400
        
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        
        query = f"""
            UPDATE events 
            SET {', '.join(update_fields)}
            WHERE event_id = %(event_id)s
            RETURNING *
        """
        
        result = execute_query(query, params, fetch='one')
        
        if result:
            return jsonify(dict(result))
        else:
            return jsonify({'error': 'Failed to update event'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/events/<event_id>', methods=['DELETE'])
def cancel_event(event_id):
    """Cancel an event (soft delete)"""
    try:
        query = """
            UPDATE events 
            SET status = 'cancelled', updated_at = CURRENT_TIMESTAMP
            WHERE event_id = %s AND status = 'active'
            RETURNING event_id, title, status
        """
        
        result = execute_query(query, (event_id,), fetch='one')
        
        if result:
            return jsonify({
                'message': 'Event cancelled successfully',
                'event': dict(result)
            })
        else:
            return jsonify({'error': 'Event not found or already cancelled'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/events/<event_id>/stats', methods=['GET'])
def get_event_stats(event_id):
    """Get detailed statistics for a specific event"""
    try:
        query = """
            SELECT 
                e.event_id,
                e.title,
                e.event_type,
                e.start_datetime,
                e.end_datetime,
                e.max_capacity,
                e.location,
                c.name as college_name,
                c.code as college_code,
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
            GROUP BY e.event_id, e.title, e.event_type, e.start_datetime, e.end_datetime, 
                     e.max_capacity, e.location, c.name, c.code
        """
        
        result = execute_query(query, (event_id,), fetch='one')
        
        if result:
            stats = dict(result)
            
            # Calculate additional metrics
            if stats['total_registrations'] > 0:
                stats['attendance_percentage'] = round(
                    (stats['total_attendance'] / stats['total_registrations']) * 100, 2
                )
            else:
                stats['attendance_percentage'] = 0
                
            if stats['max_capacity']:
                stats['capacity_utilization'] = round(
                    (stats['total_registrations'] / stats['max_capacity']) * 100, 2
                )
            else:
                stats['capacity_utilization'] = None
                
            if stats['total_attendance'] > 0:
                stats['feedback_response_rate'] = round(
                    (stats['feedback_count'] / stats['total_attendance']) * 100, 2
                )
            else:
                stats['feedback_response_rate'] = 0
            
            return jsonify(stats)
        else:
            return jsonify({'error': 'Event not found'}), 404
            
    except Exception as e:
        logger.error(f"Error getting event stats: {e}")
        return jsonify({'error': str(e)}), 500

# STUDENT MANAGEMENT ENDPOINTS

@app.route('/api/students', methods=['POST'])
def create_student():
    """Create/register a new student"""
    try:
        data = request.get_json()
        
        # Validate student data
        validation_result = validate_student_data(data)
        if not validation_result['valid']:
            return jsonify({'error': validation_result['message']}), 400
        
        query = """
            INSERT INTO students (college_id, email, name, student_number, phone, year_of_study, department)
            VALUES (%(college_id)s, %(email)s, %(name)s, %(student_number)s, %(phone)s, %(year_of_study)s, %(department)s)
            RETURNING student_id, college_id, email, name, student_number, phone, year_of_study, department, created_at
        """
        
        student_data = {
            'college_id': data['college_id'],
            'email': data['email'].lower(),
            'name': data['name'],
            'student_number': data['student_number'],
            'phone': data.get('phone'),
            'year_of_study': data.get('year_of_study'),
            'department': data.get('department')
        }
        
        result = execute_query(query, student_data, fetch='one')
        
        if result:
            return jsonify(dict(result)), 201
        else:
            return jsonify({'error': 'Failed to create student'}), 500
            
    except Exception as e:
        if 'duplicate key value violates unique constraint' in str(e):
            if 'email' in str(e):
                return jsonify({'error': 'Email address already exists'}), 409
            elif 'student_number' in str(e):
                return jsonify({'error': 'Student number already exists for this college'}), 409
        return jsonify({'error': str(e)}), 500

@app.route('/api/students', methods=['GET'])
def get_students():
    """Get all students with optional filters"""
    try:
        college_id = request.args.get('college_id')
        
        if college_id:
            query = """
                SELECT s.*, c.name as college_name, c.code as college_code,
                       COUNT(DISTINCT r.registration_id) as total_registrations,
                       COUNT(DISTINCT a.attendance_id) as events_attended
                FROM students s
                LEFT JOIN colleges c ON s.college_id = c.college_id
                LEFT JOIN registrations r ON s.student_id = r.student_id AND r.status = 'registered'
                LEFT JOIN attendance a ON r.registration_id = a.registration_id
                WHERE s.college_id = %s AND s.is_active = TRUE
                GROUP BY s.student_id, c.name, c.code
                ORDER BY s.name ASC
            """
            params = (college_id,)
        else:
            query = """
                SELECT s.*, c.name as college_name, c.code as college_code,
                       COUNT(DISTINCT r.registration_id) as total_registrations,
                       COUNT(DISTINCT a.attendance_id) as events_attended
                FROM students s
                LEFT JOIN colleges c ON s.college_id = c.college_id
                LEFT JOIN registrations r ON s.student_id = r.student_id AND r.status = 'registered'
                LEFT JOIN attendance a ON r.registration_id = a.registration_id
                WHERE s.is_active = TRUE
                GROUP BY s.student_id, c.name, c.code
                ORDER BY c.name ASC, s.name ASC
            """
            params = None
        
        students = execute_query(query, params, fetch='all')
        return jsonify([dict(student) for student in students])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/students/login', methods=['POST'])
def student_login():
    """Simple student login by email"""
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Find student by email
        query = """
            SELECT s.*, c.name as college_name, c.code as college_code
            FROM students s
            LEFT JOIN colleges c ON s.college_id = c.college_id
            WHERE s.email = %s AND s.is_active = TRUE
        """
        
        student = execute_query(query, (email,), fetch='one')
        
        if student:
            return jsonify(dict(student)), 200
        else:
            return jsonify({'error': 'Student not found with this email address'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/students/search', methods=['GET'])
def search_students():
    """Search students by name or email"""
    try:
        search_term = request.args.get('q', '').strip()
        
        if not search_term:
            return jsonify({'error': 'Search term is required'}), 400
        
        query = """
            SELECT s.*, c.name as college_name, c.code as college_code
            FROM students s
            LEFT JOIN colleges c ON s.college_id = c.college_id
            WHERE s.is_active = TRUE 
            AND (LOWER(s.name) LIKE LOWER(%s) OR LOWER(s.email) LIKE LOWER(%s) OR s.student_number LIKE %s)
            ORDER BY s.name ASC
            LIMIT 20
        """
        
        search_pattern = f'%{search_term}%'
        students = execute_query(query, (search_pattern, search_pattern, search_pattern), fetch='all')
        return jsonify([dict(student) for student in students])
        
    except Exception as e:
        logger.error(f"Error searching students: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/registrations/search', methods=['GET'])
def search_registrations():
    """Search registrations for attendance management"""
    try:
        search_term = request.args.get('q', '').strip()
        
        if not search_term:
            return jsonify({'error': 'Search term is required'}), 400
        
        query = """
            SELECT 
                r.registration_id,
                r.event_id,
                r.student_id,
                r.registered_at,
                r.status,
                s.name as student_name,
                s.email as student_email,
                s.student_number,
                e.title as event_name,
                e.event_type,
                e.start_datetime,
                c.name as college_name,
                a.attendance_id,
                a.checked_in_at,
                CASE WHEN a.attendance_id IS NOT NULL THEN 'checked_in' ELSE 'not_checked_in' END as attendance_status
            FROM registrations r
            JOIN students s ON r.student_id = s.student_id
            JOIN events e ON r.event_id = e.event_id
            JOIN colleges c ON e.college_id = c.college_id
            LEFT JOIN attendance a ON r.registration_id = a.registration_id
            WHERE r.status = 'registered'
            AND (LOWER(s.name) LIKE LOWER(%s) OR LOWER(s.email) LIKE LOWER(%s) OR LOWER(e.title) LIKE LOWER(%s))
            ORDER BY r.registered_at DESC
            LIMIT 50
        """
        
        search_pattern = f'%{search_term}%'
        registrations = execute_query(query, (search_pattern, search_pattern, search_pattern), fetch='all')
        return jsonify([dict(reg) for reg in registrations])
        
    except Exception as e:
        logger.error(f"Error searching registrations: {e}")
        return jsonify({'error': str(e)}), 500

# REGISTRATION ENDPOINTS

@app.route('/api/register', methods=['POST'])
def register_for_event():
    """Register a student for an event"""
    try:
        data = request.get_json()
        
        # Validate registration data
        validation_result = validate_registration_data(data)
        if not validation_result['valid']:
            return jsonify({'error': validation_result['message']}), 400
        
        event_id = data['event_id']
        student_id = data['student_id']
        
        # Check event capacity and registration deadline
        check_query = """
            SELECT e.max_capacity, e.registration_deadline, e.status, e.title,
                   COUNT(r.registration_id) as current_registrations
            FROM events e
            LEFT JOIN registrations r ON e.event_id = r.event_id AND r.status = 'registered'
            WHERE e.event_id = %s
            GROUP BY e.event_id, e.max_capacity, e.registration_deadline, e.status, e.title
        """
        
        event_info = execute_query(check_query, (event_id,), fetch='one')
        
        if not event_info:
            return jsonify({'error': 'Event not found'}), 404
            
        if event_info['status'] != 'active':
            return jsonify({'error': 'Event is not active for registration'}), 400
            
        # Check registration deadline
        if event_info['registration_deadline'] and datetime.now() > event_info['registration_deadline']:
            return jsonify({'error': 'Registration deadline has passed'}), 400
            
        # Check capacity
        if event_info['max_capacity'] and event_info['current_registrations'] >= event_info['max_capacity']:
            return jsonify({'error': 'Event is at full capacity'}), 400
        
        # Register student
        register_query = """
            INSERT INTO registrations (event_id, student_id)
            VALUES (%s, %s)
            RETURNING registration_id, event_id, student_id, registered_at, status
        """
        
        result = execute_query(register_query, (event_id, student_id), fetch='one')
        
        if result:
            return jsonify(dict(result)), 201
        else:
            return jsonify({'error': 'Failed to register for event'}), 500
            
    except Exception as e:
        if 'duplicate key value violates unique constraint' in str(e):
            return jsonify({'error': 'Student is already registered for this event'}), 409
        return jsonify({'error': str(e)}), 500

@app.route('/api/registrations/<registration_id>', methods=['DELETE'])
def cancel_registration(registration_id):
    """Cancel a registration"""
    try:
        query = """
            UPDATE registrations 
            SET status = 'cancelled', cancelled_at = CURRENT_TIMESTAMP,
                cancellation_reason = 'Cancelled by user'
            WHERE registration_id = %s AND status = 'registered'
            RETURNING registration_id, event_id, student_id, status
        """
        
        result = execute_query(query, (registration_id,), fetch='one')
        
        if result:
            return jsonify({
                'message': 'Registration cancelled successfully',
                'registration': dict(result)
            })
        else:
            return jsonify({'error': 'Registration not found or already cancelled'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/students/<student_id>/registrations', methods=['GET'])
def get_student_registrations(student_id):
    """Get all registrations for a specific student"""
    try:
        query = """
            SELECT 
                r.registration_id,
                r.event_id,
                r.registered_at,
                r.status,
                e.title as event_name,
                e.event_type,
                e.description,
                e.start_datetime,
                e.end_datetime,
                e.location,
                c.name as college_name,
                a.attendance_id,
                a.checked_in_at,
                a.feedback_rating,
                a.feedback_comment,
                CASE WHEN a.attendance_id IS NOT NULL THEN 'attended' ELSE 'not_attended' END as attendance_status
            FROM registrations r
            JOIN events e ON r.event_id = e.event_id
            JOIN colleges c ON e.college_id = c.college_id
            LEFT JOIN attendance a ON r.registration_id = a.registration_id
            WHERE r.student_id = %s
            ORDER BY e.start_datetime DESC
        """
        
        registrations = execute_query(query, (student_id,), fetch='all')
        return jsonify([dict(reg) for reg in registrations])
        
    except Exception as e:
        logger.error(f"Error getting student registrations: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/students/<student_id>/available-events', methods=['GET'])
def get_available_events_for_student(student_id):
    """Get events available for student registration"""
    try:
        query = """
            SELECT DISTINCT
                e.event_id,
                e.title,
                e.description,
                e.event_type,
                e.start_datetime,
                e.end_datetime,
                e.location,
                e.max_capacity,
                e.registration_deadline,
                c.name as college_name,
                c.code as college_code,
                COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) as current_registrations,
                CASE WHEN sr.registration_id IS NOT NULL THEN 'registered' ELSE 'available' END as student_status
            FROM events e
            LEFT JOIN colleges c ON e.college_id = c.college_id
            LEFT JOIN registrations r ON e.event_id = r.event_id
            LEFT JOIN registrations sr ON e.event_id = sr.event_id AND sr.student_id = %s
            WHERE e.status = 'active' 
            AND e.start_datetime > CURRENT_TIMESTAMP
            AND (e.registration_deadline IS NULL OR e.registration_deadline > CURRENT_TIMESTAMP)
            GROUP BY e.event_id, e.title, e.description, e.event_type, e.start_datetime, 
                     e.end_datetime, e.location, e.max_capacity, e.registration_deadline,
                     c.name, c.code, sr.registration_id
            ORDER BY e.start_datetime ASC
        """
        
        events = execute_query(query, (student_id,), fetch='all')
        return jsonify([dict(event) for event in events])
        
    except Exception as e:
        logger.error(f"Error getting available events: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/students/<student_id>/pending-feedback', methods=['GET'])
def get_pending_feedback(student_id):
    """Get events where student attended but hasn't given feedback"""
    try:
        query = """
            SELECT 
                a.attendance_id,
                r.registration_id,
                e.event_id,
                e.title as event_name,
                e.event_type,
                e.start_datetime,
                e.end_datetime,
                c.name as college_name,
                a.checked_in_at
            FROM attendance a
            JOIN registrations r ON a.registration_id = r.registration_id
            JOIN events e ON r.event_id = e.event_id
            JOIN colleges c ON e.college_id = c.college_id
            WHERE r.student_id = %s 
            AND a.feedback_rating IS NULL
            AND e.end_datetime < CURRENT_TIMESTAMP
            ORDER BY e.end_datetime DESC
        """
        
        pending = execute_query(query, (student_id,), fetch='all')
        return jsonify([dict(item) for item in pending])
        
    except Exception as e:
        logger.error(f"Error getting pending feedback: {e}")
        return jsonify({'error': str(e)}), 500

# ATTENDANCE ENDPOINTS

@app.route('/api/attendance', methods=['POST'])
def mark_attendance():
    """Mark attendance for a registration"""
    try:
        data = request.get_json()
        
        if not data or 'registration_id' not in data:
            return jsonify({'error': 'Missing registration_id'}), 400
        
        registration_id = data['registration_id']
        check_in_method = data.get('check_in_method', 'manual')
        
        # Check if registration exists and is active
        check_query = """
            SELECT r.registration_id, r.event_id, r.student_id, e.title as event_title,
                   s.name as student_name, e.end_datetime
            FROM registrations r
            JOIN events e ON r.event_id = e.event_id
            JOIN students s ON r.student_id = s.student_id
            WHERE r.registration_id = %s AND r.status = 'registered'
        """
        
        registration = execute_query(check_query, (registration_id,), fetch='one')
        
        if not registration:
            return jsonify({'error': 'Registration not found or not active'}), 404
        
        # Check if already checked in
        existing_attendance = execute_query(
            "SELECT attendance_id FROM attendance WHERE registration_id = %s", 
            (registration_id,), fetch='one'
        )
        
        if existing_attendance:
            return jsonify({'error': 'Student is already checked in for this event'}), 409
        
        # Mark attendance
        attendance_query = """
            INSERT INTO attendance (registration_id, check_in_method)
            VALUES (%s, %s)
            RETURNING attendance_id, registration_id, checked_in_at, check_in_method
        """
        
        result = execute_query(attendance_query, (registration_id, check_in_method), fetch='one')
        
        if result:
            attendance_dict = dict(result)
            attendance_dict['event_title'] = registration['event_title']
            attendance_dict['student_name'] = registration['student_name']
            return jsonify(attendance_dict), 201
        else:
            return jsonify({'error': 'Failed to mark attendance'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# FEEDBACK ENDPOINTS

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit feedback for an attended event"""
    try:
        data = request.get_json()
        
        # Validate feedback data
        validation_result = validate_feedback_data(data)
        if not validation_result['valid']:
            return jsonify({'error': validation_result['message']}), 400
        
        attendance_id = data['attendance_id']
        rating = data['rating']
        comment = data.get('comment', '')
        
        # Check if attendance record exists
        check_query = """
            SELECT a.attendance_id, r.event_id, e.title as event_title
            FROM attendance a
            JOIN registrations r ON a.registration_id = r.registration_id
            JOIN events e ON r.event_id = e.event_id
            WHERE a.attendance_id = %s
        """
        
        attendance = execute_query(check_query, (attendance_id,), fetch='one')
        
        if not attendance:
            return jsonify({'error': 'Attendance record not found'}), 404
        
        # Update attendance with feedback
        feedback_query = """
            UPDATE attendance 
            SET feedback_rating = %s, feedback_comment = %s, feedback_submitted_at = CURRENT_TIMESTAMP
            WHERE attendance_id = %s
            RETURNING attendance_id, feedback_rating, feedback_comment, feedback_submitted_at
        """
        
        result = execute_query(feedback_query, (rating, comment, attendance_id), fetch='one')
        
        if result:
            feedback_dict = dict(result)
            feedback_dict['event_title'] = attendance['event_title']
            return jsonify(feedback_dict), 200
        else:
            return jsonify({'error': 'Failed to submit feedback'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# COMPREHENSIVE REPORTING ENDPOINTS

@app.route('/api/reports/event-popularity', methods=['GET'])
def get_event_popularity_report():
    """Get event popularity report - events ranked by total registrations"""
    try:
        # Load SQL from file
        sql_file = os.path.join(os.path.dirname(__file__), '..', 'reports', 'event_popularity.sql')
        with open(sql_file, 'r') as f:
            query = f.read()
        
        results = execute_query(query, fetch='all')
        return jsonify([dict(row) for row in results])
        
    except Exception as e:
        logger.error(f"Error in event popularity report: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/student-participation', methods=['GET'])
def get_student_participation_report():
    """Get student participation report - student activity levels"""
    try:
        sql_file = os.path.join(os.path.dirname(__file__), '..', 'reports', 'student_participation.sql')
        with open(sql_file, 'r') as f:
            query = f.read()
        
        results = execute_query(query, fetch='all')
        return jsonify([dict(row) for row in results])
        
    except Exception as e:
        logger.error(f"Error in student participation report: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/attendance-analytics', methods=['GET'])
def get_attendance_analytics():
    """Get comprehensive attendance analytics"""
    try:
        sql_file = os.path.join(os.path.dirname(__file__), '..', 'reports', 'attendance_reports.sql')
        with open(sql_file, 'r') as f:
            query = f.read()
        
        # Extract the first query (attendance percentage per event)
        query_parts = query.split('-- 2.')
        main_query = query_parts[0].strip()
        
        results = execute_query(main_query, fetch='all')
        return jsonify([dict(row) for row in results])
        
    except Exception as e:
        logger.error(f"Error in attendance analytics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/feedback-analysis', methods=['GET'])
def get_feedback_analysis():
    """Get feedback analysis and ratings overview"""
    try:
        sql_file = os.path.join(os.path.dirname(__file__), '..', 'reports', 'feedback_reports.sql')
        with open(sql_file, 'r') as f:
            query = f.read()
        
        # Extract the first query (average feedback per event)
        query_parts = query.split('-- 2.')
        main_query = query_parts[0].strip()
        
        results = execute_query(main_query, fetch='all')
        return jsonify([dict(row) for row in results])
        
    except Exception as e:
        logger.error(f"Error in feedback analysis: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/top-active-students', methods=['GET'])
def get_top_active_students():
    """Get top 3 most active students (bonus report)"""
    try:
        sql_file = os.path.join(os.path.dirname(__file__), '..', 'reports', 'bonus_reports.sql')
        with open(sql_file, 'r') as f:
            content = f.read()
        
        # Extract the first query (top 3 most active students)
        query_parts = content.split('-- 2.')
        query = query_parts[0].strip()
        # Remove the initial comments
        query_lines = query.split('\n')
        sql_lines = []
        in_sql = False
        for line in query_lines:
            if line.strip().startswith('SELECT'):
                in_sql = True
            if in_sql:
                sql_lines.append(line)
        
        query = '\n'.join(sql_lines)
        
        results = execute_query(query, fetch='all')
        return jsonify([dict(row) for row in results])
        
    except Exception as e:
        logger.error(f"Error in top active students report: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/college-performance', methods=['GET'])
def get_college_performance():
    """Get college performance comparison"""
    try:
        query = """
            SELECT 
                c.college_id,
                c.name as college_name,
                c.code as college_code,
                COUNT(DISTINCT e.event_id) as total_events,
                COUNT(DISTINCT s.student_id) as total_students,
                COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) as total_registrations,
                COUNT(DISTINCT a.attendance_id) as total_attendance,
                CASE 
                    WHEN COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) = 0 THEN 0
                    ELSE ROUND((COUNT(DISTINCT a.attendance_id) * 100.0 / COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END)), 2)
                END as attendance_percentage,
                ROUND(AVG(a.feedback_rating), 2) as avg_feedback_rating,
                COUNT(DISTINCT CASE WHEN a.feedback_rating IS NOT NULL THEN a.attendance_id END) as feedback_responses
            FROM colleges c
            LEFT JOIN events e ON c.college_id = e.college_id AND e.status = 'active'
            LEFT JOIN students s ON c.college_id = s.college_id AND s.is_active = TRUE
            LEFT JOIN registrations r ON e.event_id = r.event_id
            LEFT JOIN attendance a ON r.registration_id = a.registration_id
            GROUP BY c.college_id, c.name, c.code
            ORDER BY avg_feedback_rating DESC, attendance_percentage DESC
        """
        
        results = execute_query(query, fetch='all')
        return jsonify([dict(row) for row in results])
        
    except Exception as e:
        logger.error(f"Error in college performance report: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/event-type-analytics', methods=['GET'])
def get_event_type_analytics():
    """Get analytics by event type"""
    try:
        query = """
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
                ROUND(AVG(a.feedback_rating), 2) as avg_rating,
                COUNT(DISTINCT CASE WHEN a.feedback_rating IS NOT NULL THEN a.attendance_id END) as feedback_responses
            FROM events e
            LEFT JOIN registrations r ON e.event_id = r.event_id
            LEFT JOIN attendance a ON r.registration_id = a.registration_id
            WHERE e.status = 'active'
            GROUP BY e.event_type
            ORDER BY avg_rating DESC, avg_attendance_percentage DESC
        """
        
        results = execute_query(query, fetch='all')
        return jsonify([dict(row) for row in results])
        
    except Exception as e:
        logger.error(f"Error in event type analytics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/system-overview', methods=['GET'])
def get_system_overview():
    """Get overall system statistics"""
    try:
        query = """
            SELECT 
                (SELECT COUNT(*) FROM colleges) as total_colleges,
                (SELECT COUNT(*) FROM events WHERE status = 'active') as total_active_events,
                (SELECT COUNT(*) FROM students WHERE is_active = TRUE) as total_active_students,
                (SELECT COUNT(*) FROM registrations WHERE status = 'registered') as total_active_registrations,
                (SELECT COUNT(*) FROM attendance) as total_attendance_records,
                (SELECT COUNT(*) FROM attendance WHERE feedback_rating IS NOT NULL) as total_feedback_responses,
                (SELECT ROUND(AVG(feedback_rating), 2) FROM attendance WHERE feedback_rating IS NOT NULL) as overall_avg_rating,
                (SELECT ROUND(
                    (COUNT(CASE WHEN status = 'registered' THEN 1 END) * 100.0 / 
                     COUNT(*)), 2
                ) FROM registrations) as overall_registration_success_rate
        """
        
        result = execute_query(query, fetch='one')
        return jsonify(dict(result))
        
    except Exception as e:
        logger.error(f"Error in system overview: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/filter', methods=['GET'])
def get_filtered_reports():
    """Get filtered reports based on query parameters"""
    try:
        college_id = request.args.get('college_id')
        event_type = request.args.get('event_type')
        report_type = request.args.get('type', 'events')
        
        if report_type == 'events':
            # Build dynamic WHERE clause
            where_conditions = ["e.status = 'active'"]
            params = {}
            
            if college_id:
                where_conditions.append("e.college_id = %(college_id)s")
                params['college_id'] = college_id
                
            if event_type:
                where_conditions.append("e.event_type = %(event_type)s")
                params['event_type'] = event_type
            
            where_clause = " AND ".join(where_conditions)
            
            query = f"""
                SELECT 
                    e.event_id,
                    e.title as event_name,
                    e.event_type,
                    c.name as college_name,
                    e.start_datetime,
                    e.max_capacity,
                    COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) as registrations,
                    COUNT(DISTINCT a.attendance_id) as attendance,
                    CASE 
                        WHEN COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END) = 0 THEN 0
                        ELSE ROUND((COUNT(DISTINCT a.attendance_id) * 100.0 / COUNT(DISTINCT CASE WHEN r.status = 'registered' THEN r.registration_id END)), 2)
                    END as attendance_percentage,
                    ROUND(AVG(a.feedback_rating), 2) as avg_rating
                FROM events e
                LEFT JOIN colleges c ON e.college_id = c.college_id
                LEFT JOIN registrations r ON e.event_id = r.event_id
                LEFT JOIN attendance a ON r.registration_id = a.registration_id
                WHERE {where_clause}
                GROUP BY e.event_id, e.title, e.event_type, c.name, e.start_datetime, e.max_capacity
                ORDER BY e.start_datetime DESC
            """
            
            results = execute_query(query, params, fetch='all')
            return jsonify([dict(row) for row in results])
            
        else:
            return jsonify({'error': 'Invalid report type'}), 400
        
    except Exception as e:
        logger.error(f"Error in filtered reports: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
