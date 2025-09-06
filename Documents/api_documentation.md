# Campus Event Management Platform - API Documentation

## Overview

The Campus Event Management Platform provides a comprehensive REST API for managing college events, student registrations, attendance tracking, and feedback collection across multiple institutions.

**Base URL**: `http://localhost:5000`

## Authentication

Currently, the API uses basic request validation. In a production environment, implement JWT or OAuth2 authentication.

## Response Format

All API responses follow this standard format:

### Success Response
```json
{
  "data": { ... },
  "message": "Success message"
}
```

### Error Response
```json
{
  "error": "Error type",
  "message": "Detailed error message"
}
```

## Status Codes

- `200` - OK
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `409` - Conflict (duplicate resource)
- `500` - Internal Server Error

## Endpoints

### 1. Health Check

#### GET /health
Check system health and database connectivity.

**Response:**
```json
{
  "status": "healthy|unhealthy",
  "timestamp": "2025-01-01T12:00:00Z",
  "database": "connected|disconnected"
}
```

---

### 2. College Management

#### POST /api/colleges
Create a new college.

**Request Body:**
```json
{
  "name": "Massachusetts Institute of Technology",
  "code": "MIT",
  "address": "77 Massachusetts Avenue",
  "city": "Cambridge",
  "state": "Massachusetts",
  "contact_email": "events@mit.edu",
  "phone": "+1-617-253-1000"
}
```

**Response (201):**
```json
{
  "college_id": "uuid",
  "name": "Massachusetts Institute of Technology",
  "code": "MIT",
  "address": "77 Massachusetts Avenue",
  "city": "Cambridge",
  "state": "Massachusetts",
  "contact_email": "events@mit.edu",
  "phone": "+1-617-253-1000",
  "created_at": "2025-01-01T12:00:00Z"
}
```

#### GET /api/colleges
Get all colleges with statistics.

**Response (200):**
```json
[
  {
    "college_id": "uuid",
    "name": "MIT",
    "code": "MIT",
    "total_events": 5,
    "total_students": 150,
    "created_at": "2025-01-01T12:00:00Z"
  }
]
```

#### GET /api/colleges/{college_id}
Get specific college details.

**Response (200):**
```json
{
  "college_id": "uuid",
  "name": "MIT",
  "code": "MIT",
  "total_events": 5,
  "total_students": 150,
  "upcoming_events": 3,
  "created_at": "2025-01-01T12:00:00Z"
}
```

---

### 3. Event Management

#### POST /api/events
Create a new event.

**Request Body:**
```json
{
  "college_id": "uuid",
  "title": "AI/ML Workshop Series",
  "description": "Comprehensive workshop on machine learning fundamentals",
  "event_type": "workshop",
  "start_datetime": "2025-02-15T10:00:00Z",
  "end_datetime": "2025-02-15T18:00:00Z",
  "location": "MIT Stata Center",
  "max_capacity": 50,
  "registration_deadline": "2025-02-10T23:59:59Z",
  "created_by": "Admin User"
}
```

**Event Types:**
- `hackathon`
- `workshop`
- `tech_talk`
- `fest`

**Response (201):**
```json
{
  "event_id": "uuid",
  "college_id": "uuid",
  "title": "AI/ML Workshop Series",
  "description": "Comprehensive workshop on machine learning fundamentals",
  "event_type": "workshop",
  "start_datetime": "2025-02-15T10:00:00Z",
  "end_datetime": "2025-02-15T18:00:00Z",
  "location": "MIT Stata Center",
  "max_capacity": 50,
  "registration_deadline": "2025-02-10T23:59:59Z",
  "status": "active",
  "created_by": "Admin User",
  "created_at": "2025-01-01T12:00:00Z"
}
```

#### GET /api/events
Get all events with optional filters.

**Query Parameters:**
- `college_id` (optional) - Filter by college
- `event_type` (optional) - Filter by event type
- `status` (optional) - Filter by status (default: 'active')

**Response (200):**
```json
[
  {
    "event_id": "uuid",
    "title": "AI/ML Workshop Series",
    "event_type": "workshop",
    "start_datetime": "2025-02-15T10:00:00Z",
    "college_name": "MIT",
    "registration_count": 25,
    "attendance_count": 20,
    "avg_rating": 4.5
  }
]
```

#### GET /api/events/{event_id}
Get specific event details with statistics.

**Response (200):**
```json
{
  "event_id": "uuid",
  "title": "AI/ML Workshop Series",
  "event_type": "workshop",
  "start_datetime": "2025-02-15T10:00:00Z",
  "end_datetime": "2025-02-15T18:00:00Z",
  "college_name": "MIT",
  "max_capacity": 50,
  "registration_count": 25,
  "attendance_count": 20,
  "attendance_percentage": 80.0,
  "avg_rating": 4.5,
  "feedback_count": 18
}
```

#### PUT /api/events/{event_id}
Update an event.

**Request Body:** Same as POST, all fields optional
**Response (200):** Updated event object

#### DELETE /api/events/{event_id}
Cancel an event (soft delete).

**Response (200):**
```json
{
  "message": "Event cancelled successfully",
  "event": {
    "event_id": "uuid",
    "title": "Event Title",
    "status": "cancelled"
  }
}
```

---

### 4. Student Management

#### POST /api/students
Register a new student.

**Request Body:**
```json
{
  "college_id": "uuid",
  "email": "john.doe@mit.edu",
  "name": "John Doe",
  "student_number": "MIT001",
  "phone": "+1-555-0123",
  "year_of_study": 3,
  "department": "Computer Science"
}
```

**Response (201):**
```json
{
  "student_id": "uuid",
  "college_id": "uuid",
  "email": "john.doe@mit.edu",
  "name": "John Doe",
  "student_number": "MIT001",
  "phone": "+1-555-0123",
  "year_of_study": 3,
  "department": "Computer Science",
  "created_at": "2025-01-01T12:00:00Z"
}
```

#### GET /api/students
Get all students with optional college filter.

**Query Parameters:**
- `college_id` (optional) - Filter by college

**Response (200):**
```json
[
  {
    "student_id": "uuid",
    "name": "John Doe",
    "email": "john.doe@mit.edu",
    "college_name": "MIT",
    "total_registrations": 5,
    "events_attended": 4
  }
]
```

---

### 5. Registration Management

#### POST /api/register
Register a student for an event.

**Request Body:**
```json
{
  "event_id": "uuid",
  "student_id": "uuid"
}
```

**Response (201):**
```json
{
  "registration_id": "uuid",
  "event_id": "uuid",
  "student_id": "uuid",
  "registered_at": "2025-01-01T12:00:00Z",
  "status": "registered"
}
```

**Error Cases:**
- Event at capacity: `400 - Event is at full capacity`
- Registration deadline passed: `400 - Registration deadline has passed`
- Duplicate registration: `409 - Student is already registered for this event`

#### DELETE /api/registrations/{registration_id}
Cancel a registration.

**Response (200):**
```json
{
  "message": "Registration cancelled successfully",
  "registration": {
    "registration_id": "uuid",
    "status": "cancelled"
  }
}
```

---

### 6. Attendance Management

#### POST /api/attendance
Mark attendance for a registration.

**Request Body:**
```json
{
  "registration_id": "uuid",
  "check_in_method": "manual"
}
```

**Check-in Methods:**
- `manual` (default)
- `qr_code`
- `rfid`

**Response (201):**
```json
{
  "attendance_id": "uuid",
  "registration_id": "uuid",
  "checked_in_at": "2025-02-15T10:30:00Z",
  "check_in_method": "manual",
  "event_title": "AI/ML Workshop Series",
  "student_name": "John Doe"
}
```

**Error Cases:**
- Registration not found: `404 - Registration not found or not active`
- Already checked in: `409 - Student is already checked in for this event`

---

### 7. Feedback Management

#### POST /api/feedback
Submit feedback for an attended event.

**Request Body:**
```json
{
  "attendance_id": "uuid",
  "rating": 5,
  "comment": "Excellent workshop! Very informative."
}
```

**Validation:**
- `rating`: Required, integer between 1-5
- `comment`: Optional, max 1000 characters

**Response (200):**
```json
{
  "attendance_id": "uuid",
  "feedback_rating": 5,
  "feedback_comment": "Excellent workshop! Very informative.",
  "feedback_submitted_at": "2025-02-15T20:00:00Z",
  "event_title": "AI/ML Workshop Series"
}
```

---

### 8. Reporting Endpoints

#### GET /api/reports/event-popularity
Get events ranked by popularity (registrations).

**Response (200):**
```json
[
  {
    "event_id": "uuid",
    "event_name": "AI/ML Workshop Series",
    "event_type": "workshop",
    "college_name": "MIT",
    "start_datetime": "2025-02-15T10:00:00Z",
    "total_registrations": 45,
    "active_registrations": 42,
    "capacity_utilization": "84%",
    "registration_status": "Nearly Full"
  }
]
```

#### GET /api/reports/student-participation
Get student participation statistics.

**Response (200):**
```json
[
  {
    "student_id": "uuid",
    "student_name": "John Doe",
    "email": "john.doe@mit.edu",
    "college_name": "MIT",
    "total_registrations": 5,
    "events_attended": 4,
    "attendance_percentage": 80.0,
    "avg_feedback_rating": 4.2,
    "activity_level": "Active"
  }
]
```

---

## Data Models

### College
```json
{
  "college_id": "UUID",
  "name": "string (max 200)",
  "code": "string (max 10, unique)",
  "address": "string",
  "city": "string (max 100)",
  "state": "string (max 50)",
  "contact_email": "string (email format)",
  "phone": "string (max 20)",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### Event
```json
{
  "event_id": "UUID",
  "college_id": "UUID (foreign key)",
  "title": "string (max 200, required)",
  "description": "text",
  "event_type": "enum [hackathon, workshop, tech_talk, fest]",
  "start_datetime": "timestamp (required)",
  "end_datetime": "timestamp (required)",
  "location": "string (max 300)",
  "max_capacity": "integer (nullable)",
  "registration_deadline": "timestamp",
  "status": "enum [active, cancelled, completed, draft]",
  "created_by": "string (max 255)",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### Student
```json
{
  "student_id": "UUID",
  "college_id": "UUID (foreign key)",
  "email": "string (max 255, unique, required)",
  "name": "string (max 200, required)",
  "student_number": "string (max 50, required)",
  "phone": "string (max 20)",
  "year_of_study": "integer (1-4)",
  "department": "string (max 100)",
  "is_active": "boolean",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### Registration
```json
{
  "registration_id": "UUID",
  "event_id": "UUID (foreign key)",
  "student_id": "UUID (foreign key)",
  "registered_at": "timestamp",
  "status": "enum [registered, cancelled, waitlisted]",
  "registration_source": "string (max 50)",
  "cancelled_at": "timestamp",
  "cancellation_reason": "text"
}
```

### Attendance
```json
{
  "attendance_id": "UUID",
  "registration_id": "UUID (foreign key, unique)",
  "checked_in_at": "timestamp",
  "checked_out_at": "timestamp",
  "check_in_method": "enum [manual, qr_code, rfid]",
  "feedback_rating": "integer (1-5)",
  "feedback_comment": "text",
  "feedback_submitted_at": "timestamp"
}
```

## Error Handling

### Common Error Responses

**400 Bad Request:**
```json
{
  "error": "Bad request",
  "message": "Missing required field: title"
}
```

**404 Not Found:**
```json
{
  "error": "Not found",
  "message": "Event not found"
}
```

**409 Conflict:**
```json
{
  "error": "Duplicate entry",
  "message": "Student is already registered for this event"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Internal server error",
  "message": "Database connection failed"
}
```

## Rate Limiting

In production, implement rate limiting:
- General API calls: 100 requests/minute
- Registration endpoints: 10 requests/minute
- Feedback submissions: 5 requests/minute

## Pagination

For endpoints returning large datasets, implement pagination:

**Query Parameters:**
- `page` - Page number (default: 1)
- `per_page` - Items per page (default: 20, max: 100)

**Response Format:**
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

## Testing

Use tools like Postman, curl, or automated testing frameworks to test the API:

```bash
# Test health endpoint
curl -X GET http://localhost:5000/health

# Create a college
curl -X POST http://localhost:5000/api/colleges \
  -H "Content-Type: application/json" \
  -d '{"name":"Test University","code":"TEST"}'

# Get all events
curl -X GET http://localhost:5000/api/events
```
