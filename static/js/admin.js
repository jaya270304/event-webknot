// Admin Portal Specific JavaScript Functions

let currentAttendanceId = null;
let currentRegistrationId = null;

// College Management Functions
async function createCollege() {
    const name = document.getElementById('college-name').value.trim();
    const code = document.getElementById('college-code').value.trim();
    
    if (!name || !code) {
        showMessage('Please fill in all required fields.', 'error');
        return;
    }
    
    try {
        const result = await apiPost('/api/colleges', { name, code });
        showMessage(`College "${result.name}" created successfully!`, 'success');
        
        // Clear form
        document.getElementById('college-name').value = '';
        document.getElementById('college-code').value = '';
        
        // Reload colleges
        await loadColleges();
        
    } catch (error) {
        showMessage('Error creating college: ' + error.message, 'error');
    }
}

// Event Management Functions
async function createEvent() {
    const collegeId = document.getElementById('event-college').value;
    const title = document.getElementById('event-title').value.trim();
    const eventType = document.getElementById('event-type').value;
    const description = document.getElementById('event-description').value.trim();
    const startDateTime = document.getElementById('event-start').value;
    const endDateTime = document.getElementById('event-end').value;
    const capacity = document.getElementById('event-capacity').value;
    
    if (!collegeId || !title || !eventType || !startDateTime || !endDateTime) {
        showMessage('Please fill in all required fields.', 'error');
        return;
    }
    
    try {
        const eventData = {
            college_id: collegeId,
            title,
            event_type: eventType,
            description,
            start_datetime: startDateTime,
            end_datetime: endDateTime,
            max_capacity: capacity ? parseInt(capacity) : null
        };
        
        const result = await apiPost('/api/events', eventData);
        showMessage(`Event "${result.title}" created successfully!`, 'success');
        
        // Clear form
        document.getElementById('event-title').value = '';
        document.getElementById('event-description').value = '';
        document.getElementById('event-start').value = '';
        document.getElementById('event-end').value = '';
        document.getElementById('event-capacity').value = '';
        
        // Reload events
        await loadEvents();
        
    } catch (error) {
        showMessage('Error creating event: ' + error.message, 'error');
    }
}

// Note: Student registration functionality has been removed from admin portal
// Students can register themselves through the student portal

// Attendance Management Functions
async function searchRegistrations() {
    const searchTerm = document.getElementById('attendance-search').value.trim();
    
    if (!searchTerm) {
        showMessage('Please enter a search term (student name, email, or event name).', 'error');
        return;
    }
    
    try {
        const registrations = await apiGet(`/api/registrations/search?q=${encodeURIComponent(searchTerm)}`);
        
        const registrationsList = document.getElementById('registrations-list');
        
        if (registrations.length === 0) {
            registrationsList.innerHTML = 
                '<div class="message info">No registrations found matching your search.</div>';
            return;
        }
        
        registrationsList.innerHTML = `
            <h4>Found Registrations (${registrations.length}):</h4>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Student</th>
                            <th>Event</th>
                            <th>College</th>
                            <th>Date</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${registrations.map(reg => `
                            <tr>
                                <td>
                                    <strong>${reg.student_name}</strong><br/>
                                    <small>${reg.student_email}</small><br/>
                                    <small>ID: ${reg.student_number}</small>
                                </td>
                                <td><strong>${reg.event_name}</strong><br/><small>${reg.event_type.toUpperCase()}</small></td>
                                <td>${reg.college_name}</td>
                                <td>${formatDateTime(reg.start_datetime)}</td>
                                <td>
                                    <span class="event-type ${reg.attendance_status === 'checked_in' ? 'fest' : 'hackathon'}">
                                        ${reg.attendance_status === 'checked_in' ? 'CHECKED IN' : 'REGISTERED'}
                                    </span>
                                    ${reg.checked_in_at ? `<br/><small>at ${formatDateTime(reg.checked_in_at)}</small>` : ''}
                                </td>
                                <td>
                                    ${reg.attendance_status === 'checked_in' ? 
                                        '<span class="event-type fest">Complete</span>' :
                                        `<button class="btn btn-success" onclick="markAttendance('${reg.registration_id}', '${reg.student_name}', '${reg.event_name}')">Check In</button>`
                                    }
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
    } catch (error) {
        showMessage('Error searching registrations: ' + error.message, 'error');
        document.getElementById('registrations-list').innerHTML = 
            '<div class="message error">Error loading registrations: ' + error.message + '</div>';
    }
}

async function markAttendance(registrationId, studentName, eventTitle) {
    try {
        const attendanceData = {
            registration_id: registrationId,
            check_in_method: 'manual'
        };
        
        const result = await apiPost('/api/attendance', attendanceData);
        showMessage(`${studentName} checked in successfully for ${eventTitle}!`, 'success');
        
        // Show feedback option
        setTimeout(() => {
            if (confirm('Would you like to collect feedback for this event?')) {
                openFeedbackModal(result.attendance_id, eventTitle);
            }
        }, 1000);
        
        // Refresh the registrations view
        const eventId = document.querySelector(`[data-event-id]`)?.dataset.eventId;
        if (eventId) {
            viewEventRegistrations(eventId);
        }
        
    } catch (error) {
        showMessage('Error checking in student: ' + error.message, 'error');
    }
}

function openFeedbackModal(attendanceId, eventTitle) {
    currentAttendanceId = attendanceId;
    const modal = document.getElementById('feedback-modal');
    const modalTitle = modal.querySelector('h3');
    modalTitle.textContent = `Submit Feedback for ${eventTitle}`;
    modal.style.display = 'block';
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
        showMessage('No attendance record found.', 'error');
        return;
    }
    
    try {
        const feedbackData = {
            attendance_id: currentAttendanceId,
            rating: rating,
            comment: comment
        };
        
        const result = await apiPost('/api/feedback', feedbackData);
        showMessage(`Feedback submitted: ${rating} stars for ${result.event_title}`, 'success');
        
        // Clear form and close modal
        document.getElementById('feedback-comment').value = '';
        document.querySelectorAll('#rating-stars .star').forEach(star => {
            star.classList.remove('filled');
        });
        
        closeModal('feedback-modal');
        currentAttendanceId = null;
        
    } catch (error) {
        showMessage('Error submitting feedback: ' + error.message, 'error');
    }
}

async function viewEventRegistrations(eventId) {
    try {
        // Get event details
        const event = await apiGet(`/api/events/${eventId}`);
        
        // For demo, we'll create some sample registrations if none exist
        // In production, this would fetch real registration data
        const registrationsList = document.getElementById('registrations-list');
        
        // Since we don't have a dedicated registrations endpoint yet, 
        // we'll show a simulated view with real event data
        registrationsList.innerHTML = `
            <div class="card" data-event-id="${eventId}">
                <h4>Event Registrations: ${event.title}</h4>
                <p><strong>Total Registrations:</strong> ${event.registration_count || 0}</p>
                <p><strong>Total Attendance:</strong> ${event.attendance_count || 0}</p>
                <p><strong>Attendance Rate:</strong> ${event.attendance_percentage || 0}%</p>
                
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Student Name</th>
                                <th>Email</th>
                                <th>Registration Date</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${generateSampleRegistrations(eventId, event.title)}
                        </tbody>
                    </table>
                </div>
                
                <div class="btn-group" style="margin-top: 1rem;">
                    <button class="btn" onclick="viewEventStats('${eventId}')">
                        📊 View Detailed Stats
                    </button>
                    <button class="btn btn-info" onclick="searchRegistrations()">« Back to Search</button>
                </div>
            </div>
        `;
        
    } catch (error) {
        showMessage('Error loading registrations: ' + error.message, 'error');
    }
}

// Helper function to generate sample registrations for demo
function generateSampleRegistrations(eventId, eventTitle) {
    const sampleRegistrations = [
        { name: 'John Doe', email: 'john.doe@college.edu', status: 'registered', regId: 'reg-001' },
        { name: 'Jane Smith', email: 'jane.smith@college.edu', status: 'registered', regId: 'reg-002' },
        { name: 'Mike Johnson', email: 'mike.johnson@college.edu', status: 'attended', regId: 'reg-003' },
        { name: 'Sarah Wilson', email: 'sarah.wilson@college.edu', status: 'registered', regId: 'reg-004' },
        { name: 'David Brown', email: 'david.brown@college.edu', status: 'registered', regId: 'reg-005' }
    ];
    
    return sampleRegistrations.map(reg => `
        <tr>
            <td>${reg.name}</td>
            <td>${reg.email}</td>
            <td>${formatDate(new Date().toISOString())}</td>
            <td>
                <span class="event-type ${reg.status === 'attended' ? 'tech_talk' : 'hackathon'}">
                    ${reg.status.charAt(0).toUpperCase() + reg.status.slice(1)}
                </span>
            </td>
            <td>
                ${reg.status === 'registered' 
                    ? `<button class="btn btn-success" onclick="markAttendance('${reg.regId}', '${reg.name}', '${eventTitle}')">Check-in</button>`
                    : `<button class="btn" disabled>Already Attended</button>`
                }
            </td>
        </tr>
    `).join('');
}

// Event editing functions
function editEvent(eventId) {
    showMessage('Event editing feature would be implemented here. For now, use the cancel/create workflow.', 'info');
}

async function viewEventStats(eventId) {
    try {
        const stats = await apiGet(`/api/events/${eventId}/stats`);
        
        const statsHtml = `
            <div class="card">
                <h4>📊 Event Statistics: ${stats.title}</h4>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">${stats.total_registrations}</div>
                        <div class="stat-label">Total Registrations</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${stats.total_attendance}</div>
                        <div class="stat-label">Attendees</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${stats.attendance_percentage}%</div>
                        <div class="stat-label">Attendance Rate</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${stats.avg_rating || 'N/A'}</div>
                        <div class="stat-label">Average Rating</div>
                    </div>
                </div>
                <div class="event-meta">
                    <p><strong>Event Type:</strong> ${stats.event_type}</p>
                    <p><strong>Date:</strong> ${formatDateTime(stats.start_datetime)} - ${formatDateTime(stats.end_datetime)}</p>
                    <p><strong>Feedback Count:</strong> ${stats.feedback_count} submissions</p>
                </div>
            </div>
        `;
        
        // Show stats in the events list area
        document.getElementById('events-list').innerHTML = statsHtml;
        showMessage('Event statistics loaded successfully!', 'success');
        
    } catch (error) {
        showMessage('Error loading event statistics: ' + error.message, 'error');
    }
}

// Setup modal functionality
function setupModal() {
    const modal = document.getElementById('feedback-modal');
    const closeBtn = modal.querySelector('.close');
    
    closeBtn.onclick = function() {
        closeModal('feedback-modal');
    };
    
    // Setup star rating
    setupStarRating();
}
