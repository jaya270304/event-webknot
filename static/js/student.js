// Student Portal Specific JavaScript Functions

let currentStudent = null;
let selectedEventId = null;

// Student Authentication (Real implementation)
async function loginStudent() {
    const email = document.getElementById('student-email-login').value.trim();
    
    if (!email) {
        showMessage('Please enter your email address.', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/students/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: email })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Store in localStorage for session persistence
            localStorage.setItem('currentStudent', JSON.stringify(data));
            
            showStudentDashboard(data);
            showMessage(`Welcome back, ${data.name}!`, 'success');
        } else {
            showMessage(data.error || 'Login failed. Please check your email.', 'error');
        }
        
    } catch (error) {
        showMessage('Error logging in: ' + error.message, 'error');
    }
}

function showStudentDashboard(student) {
    currentStudent = student;
    
    // Hide login section and show dashboard
    document.getElementById('login-section').style.display = 'none';
    document.getElementById('student-dashboard').style.display = 'block';
    
    // Show logout button
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.style.display = 'inline-block';
    }
    
    // Update student name
    document.getElementById('student-name-display').textContent = student.name;
    
    // Load student data
    loadAvailableEvents();
    loadMyRegistrations();
    loadPendingFeedback();
}

async function loadAvailableEvents() {
    try {
        if (!currentStudent) return;
        
        const events = await apiGet(`/api/students/${currentStudent.student_id}/available-events`);
        
        const container = document.getElementById('available-events');
        
        if (events.length === 0) {
            container.innerHTML = '<div class="message info">No events available for registration at the moment.</div>';
            return;
        }
        
        container.innerHTML = events.map(event => `
            <div class="card event-card fade-in">
                <div class="event-header">
                    <div>
                        <h4>${event.title}</h4>
                        <span class="event-type ${event.event_type}">${event.event_type.replace('_', ' ').toUpperCase()}</span>
                        ${event.student_status === 'registered' ? '<span class="event-type fest">REGISTERED</span>' : ''}
                    </div>
                </div>
                <p>${event.description || 'No description available'}</p>
                <div class="event-meta">
                    <p><strong>📅 Date:</strong> ${formatDateTime(event.start_datetime)}</p>
                    <p><strong>🏫 College:</strong> ${event.college_name}</p>
                    ${event.max_capacity ? `<p><strong>👥 Capacity:</strong> ${event.current_registrations}/${event.max_capacity} students</p>` : `<p><strong>👥 Registered:</strong> ${event.current_registrations} students</p>`}
                    ${event.location ? `<p><strong>📍 Location:</strong> ${event.location}</p>` : ''}
                </div>
                <div class="btn-group">
                    ${event.student_status === 'registered' ? 
                        '<button class="btn btn-secondary" disabled>Already Registered</button>' :
                        `<button class="btn btn-success" onclick="openRegistrationModal('${event.event_id}')">Register Now</button>`
                    }
                    <button class="btn" onclick="viewEventDetails('${event.event_id}')">
                        View Details
                    </button>
                </div>
            </div>
        `).join('');
        
        // Store events for registration modal
        sessionStorage.setItem('availableEvents', JSON.stringify(events));
        
    } catch (error) {
        document.getElementById('available-events').innerHTML = 
            '<div class="message error">Error loading events: ' + error.message + '</div>';
        console.error('Error loading available events:', error);
    }
}

async function loadMyRegistrations() {
    try {
        if (!currentStudent) return;
        
        const registrations = await apiGet(`/api/students/${currentStudent.student_id}/registrations`);
        
        const container = document.getElementById('my-registrations');
        
        if (registrations.length === 0) {
            container.innerHTML = '<div class="message info">You haven\'t registered for any events yet.</div>';
            return;
        }
        
        container.innerHTML = `
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Event</th>
                            <th>Type</th>
                            <th>College</th>
                            <th>Date</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${registrations.map(reg => {
                            const eventDate = new Date(reg.start_datetime);
                            const now = new Date();
                            const canCancel = reg.status === 'registered' && eventDate > now;
                            const needsFeedback = reg.attendance_status === 'attended' && !reg.feedback_rating;
                            
                            return `
                            <tr>
                                <td><strong>${reg.event_name}</strong></td>
                                <td><span class="event-type ${reg.event_type}">${reg.event_type.toUpperCase()}</span></td>
                                <td>${reg.college_name}</td>
                                <td>${formatDateTime(reg.start_datetime)}</td>
                                <td>
                                    <span class="event-type ${reg.attendance_status === 'attended' ? 'fest' : 'hackathon'}">
                                        ${reg.attendance_status === 'attended' ? 'ATTENDED' : reg.status.toUpperCase()}
                                    </span>
                                    ${reg.feedback_rating ? `<br/><small>Rated: ${reg.feedback_rating}⭐</small>` : ''}
                                </td>
                                <td>
                                    ${canCancel ? 
                                        `<button class="btn btn-danger" onclick="cancelRegistration('${reg.registration_id}')">Cancel</button>` :
                                        needsFeedback ? 
                                            `<button class="btn btn-warning" onclick="openStudentFeedbackModal('${reg.registration_id}', '${reg.event_name}')">Give Feedback</button>` :
                                            '<span class="event-type">Complete</span>'
                                    }
                                </td>
                            </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
    } catch (error) {
        document.getElementById('my-registrations').innerHTML = 
            '<div class="message error">Error loading your registrations: ' + error.message + '</div>';
        console.error('Error loading registrations:', error);
    }
}

async function loadPendingFeedback() {
    try {
        if (!currentStudent) return;
        
        const pendingEvents = await apiGet(`/api/students/${currentStudent.student_id}/pending-feedback`);
        
        const container = document.getElementById('pending-feedback');
        
        if (pendingEvents.length === 0) {
            container.innerHTML = '<div class="message info">No pending feedback at the moment.</div>';
            return;
        }
        
        container.innerHTML = pendingEvents.map(event => `
            <div class="card">
                <h5>${event.event_name}</h5>
                <p>Please share your experience from this ${event.event_type}.</p>
                <p class="event-meta"><strong>Date:</strong> ${formatDateTime(event.start_datetime)}</p>
                <p class="event-meta"><strong>College:</strong> ${event.college_name}</p>
                <button class="btn btn-warning" onclick="openStudentFeedbackModal('${event.attendance_id}', '${event.event_name}')">
                    Submit Feedback
                </button>
            </div>
        `).join('');
        
    } catch (error) {
        document.getElementById('pending-feedback').innerHTML = 
            '<div class="message error">Error loading pending feedback: ' + error.message + '</div>';
        console.error('Error loading pending feedback:', error);
    }
}

// Event Registration Functions
function openRegistrationModal(eventId) {
    selectedEventId = eventId;
    
    // For prototype, get event details from loaded events
    const events = JSON.parse(sessionStorage.getItem('availableEvents') || '[]');
    const event = events.find(e => e.event_id === eventId);
    
    if (event) {
        document.getElementById('modal-event-title').textContent = event.title;
        document.getElementById('modal-event-description').textContent = event.description || 'No description available';
        document.getElementById('modal-event-type').textContent = event.event_type.replace('_', ' ').toUpperCase();
        document.getElementById('modal-event-date').textContent = formatDateTime(event.start_datetime);
        document.getElementById('modal-event-college').textContent = event.college_name;
    }
    
    document.getElementById('registration-modal').style.display = 'block';
}

async function confirmRegistration() {
    if (!currentStudent || !selectedEventId) {
        showMessage('Registration error. Please try again.', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                event_id: selectedEventId,
                student_id: currentStudent.student_id
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Registration successful! You are now registered for this event.', 'success');
            closeModal('registration-modal');
            
            // Reload both available events and registrations
            setTimeout(() => {
                loadAvailableEvents();
                loadMyRegistrations();
            }, 1000);
        } else {
            showMessage(data.error || 'Registration failed. Please try again.', 'error');
        }
        
    } catch (error) {
        showMessage('Error registering for event: ' + error.message, 'error');
    }
}

async function cancelRegistration(registrationId) {
    if (!confirm('Are you sure you want to cancel your registration for this event?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/registrations/${registrationId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Registration cancelled successfully.', 'success');
            
            // Reload both available events and registrations
            setTimeout(() => {
                loadAvailableEvents();
                loadMyRegistrations();
            }, 1000);
        } else {
            showMessage(data.error || 'Failed to cancel registration.', 'error');
        }
        
    } catch (error) {
        showMessage('Error cancelling registration: ' + error.message, 'error');
    }
}

// Feedback Functions
let currentAttendanceId = null;

function openStudentFeedbackModal(attendanceId, eventName) {
    currentAttendanceId = attendanceId;
    
    // Set event title for feedback
    document.getElementById('feedback-event-title').textContent = eventName || 'Event Feedback';
    
    document.getElementById('feedback-modal').style.display = 'block';
}

async function submitFeedback() {
    const stars = document.querySelectorAll('#rating-stars .star.filled');
    const rating = stars.length;
    const comment = document.getElementById('feedback-comment').value.trim();
    
    if (rating === 0) {
        showMessage('Please select a rating.', 'error');
        return;
    }
    
    if (!currentAttendanceId) {
        showMessage('Error: No attendance record found.', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                attendance_id: currentAttendanceId,
                rating: rating,
                comment: comment
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(`Thank you for your feedback! Rating: ${rating} stars`, 'success');
            
            // Clear form and close modal
            document.getElementById('feedback-comment').value = '';
            document.querySelectorAll('#rating-stars .star').forEach(star => {
                star.classList.remove('filled');
            });
            
            closeModal('feedback-modal');
            
            // Reload pending feedback and registrations
            setTimeout(() => {
                loadPendingFeedback();
                loadMyRegistrations();
            }, 1000);
        } else {
            showMessage(data.error || 'Failed to submit feedback.', 'error');
        }
        
    } catch (error) {
        showMessage('Error submitting feedback: ' + error.message, 'error');
    }
}

// Utility Functions
function viewEventDetails(eventId) {
    // For prototype, just show a message
    showMessage('Event details view would show full event information, location, agenda, etc.', 'info');
}

function logout() {
    localStorage.removeItem('currentStudent');
    currentStudent = null;
    
    // Show login section and hide dashboard
    document.getElementById('login-section').style.display = 'block';
    document.getElementById('student-dashboard').style.display = 'none';
    
    // Hide logout button
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.style.display = 'none';
    }
    
    showMessage('You have been logged out successfully.', 'info');
}
