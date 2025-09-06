// Campus Event Management Platform - Shared JavaScript Functions

// API Base URL
const API_BASE = '';

// Utility Functions
function showMessage(message, type = 'info') {
    const messageDiv = document.getElementById('message');
    if (messageDiv) {
        messageDiv.innerHTML = `<div class="message ${type}">${message}</div>`;
        setTimeout(() => {
            messageDiv.innerHTML = '';
        }, 5000);
    }
}

function formatDateTime(dateTimeString) {
    const date = new Date(dateTimeString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// API Helper Functions
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(API_BASE + url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'API request failed');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

async function apiGet(url) {
    return apiRequest(url, { method: 'GET' });
}

async function apiPost(url, data) {
    return apiRequest(url, {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

async function apiPut(url, data) {
    return apiRequest(url, {
        method: 'PUT',
        body: JSON.stringify(data)
    });
}

async function apiDelete(url) {
    return apiRequest(url, { method: 'DELETE' });
}

// College Management Functions
async function loadColleges() {
    try {
        const colleges = await apiGet('/api/colleges');
        
        // Update college dropdowns
        updateCollegeDropdowns(colleges);
        
        // Update colleges table if it exists
        const collegesTable = document.getElementById('colleges-table');
        if (collegesTable) {
            if (colleges.length === 0) {
                collegesTable.innerHTML = '<tr><td colspan="4" class="loading">No colleges found. Add some colleges to get started.</td></tr>';
            } else {
                collegesTable.innerHTML = colleges.map(college => `
                    <tr>
                        <td>${college.name}</td>
                        <td><span class="event-type">${college.code}</span></td>
                        <td>${formatDate(college.created_at)}</td>
                        <td>
                            <button class="btn btn-success" onclick="viewCollegeEvents('${college.college_id}')">View Events</button>
                        </td>
                    </tr>
                `).join('');
            }
        }
        
        return colleges;
    } catch (error) {
        showMessage('Error loading colleges: ' + error.message, 'error');
        return [];
    }
}

function updateCollegeDropdowns(colleges) {
    const dropdowns = [
        'event-college',
        'student-college',
        'report-college'
    ];
    
    dropdowns.forEach(dropdownId => {
        const dropdown = document.getElementById(dropdownId);
        if (dropdown) {
            // Keep the first option (usually "Choose a college..." or "All Colleges")
            const firstOption = dropdown.querySelector('option').outerHTML;
            dropdown.innerHTML = firstOption + colleges.map(college => 
                `<option value="${college.college_id}">${college.name} (${college.code})</option>`
            ).join('');
        }
    });
}

async function createCollege() {
    const name = document.getElementById('college-name').value.trim();
    const code = document.getElementById('college-code').value.trim().toUpperCase();
    
    if (!name || !code) {
        showMessage('Please fill in both college name and code.', 'error');
        return;
    }
    
    try {
        await apiPost('/api/colleges', { name, code });
        showMessage('College added successfully!', 'success');
        
        // Clear form
        document.getElementById('college-name').value = '';
        document.getElementById('college-code').value = '';
        
        // Reload colleges
        loadColleges();
    } catch (error) {
        showMessage('Error creating college: ' + error.message, 'error');
    }
}

// Event Management Functions
async function loadEvents() {
    try {
        const events = await apiGet('/api/events');
        displayEvents(events, 'events-list');
        return events;
    } catch (error) {
        console.error('Error loading events:', error);
        const eventsContainer = document.getElementById('events-list');
        if (eventsContainer) {
            eventsContainer.innerHTML = '<div class="message error">Error loading events</div>';
        }
        return [];
    }
}

function displayEvents(events, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    if (events.length === 0) {
        container.innerHTML = '<div class="message info">No events found.</div>';
        return;
    }
    
    container.innerHTML = events.map(event => `
        <div class="card event-card fade-in">
            <div class="event-header">
                <div>
                    <h4>${event.title}</h4>
                    <span class="event-type ${event.event_type}">${event.event_type.replace('_', ' ').toUpperCase()}</span>
                </div>
            </div>
            <p>${event.description || 'No description available'}</p>
            <div class="event-meta">
                <p><strong>📅 Date:</strong> ${formatDateTime(event.start_datetime)} - ${formatDateTime(event.end_datetime)}</p>
                <p><strong>🏫 College:</strong> ${event.college_name}</p>
                ${event.max_capacity ? `<p><strong>👥 Capacity:</strong> ${event.max_capacity} students</p>` : ''}
            </div>
            <div class="btn-group">
                <button class="btn" onclick="viewEventStats('${event.event_id}')">View Stats</button>
                <button class="btn btn-warning" onclick="editEvent('${event.event_id}')">Edit</button>
                <button class="btn btn-danger" onclick="cancelEvent('${event.event_id}')">Cancel</button>
            </div>
        </div>
    `).join('');
}

async function createEvent() {
    const collegeId = document.getElementById('event-college').value;
    const title = document.getElementById('event-title').value.trim();
    const description = document.getElementById('event-description').value.trim();
    const eventType = document.getElementById('event-type').value;
    const startDateTime = document.getElementById('event-start').value;
    const endDateTime = document.getElementById('event-end').value;
    const maxCapacity = document.getElementById('event-capacity').value;
    
    if (!collegeId || !title || !startDateTime || !endDateTime) {
        showMessage('Please fill in all required fields.', 'error');
        return;
    }
    
    if (new Date(startDateTime) >= new Date(endDateTime)) {
        showMessage('End date must be after start date.', 'error');
        return;
    }
    
    try {
        const eventData = {
            college_id: collegeId,
            title,
            description,
            event_type: eventType,
            start_datetime: startDateTime,
            end_datetime: endDateTime,
            max_capacity: maxCapacity ? parseInt(maxCapacity) : null
        };
        
        await apiPost('/api/events', eventData);
        showMessage('Event created successfully!', 'success');
        
        // Clear form
        document.getElementById('event-title').value = '';
        document.getElementById('event-description').value = '';
        document.getElementById('event-start').value = '';
        document.getElementById('event-end').value = '';
        document.getElementById('event-capacity').value = '';
        
        // Reload events
        loadEvents();
    } catch (error) {
        showMessage('Error creating event: ' + error.message, 'error');
    }
}

async function viewCollegeEvents(collegeId) {
    try {
        const events = await apiGet(`/api/colleges/${collegeId}/events`);
        showMessage(`Found ${events.length} events for this college.`, 'info');
        displayEvents(events, 'events-list');
    } catch (error) {
        showMessage('Error loading college events: ' + error.message, 'error');
    }
}

async function cancelEvent(eventId) {
    if (!confirm('Are you sure you want to cancel this event?')) {
        return;
    }
    
    try {
        await apiDelete(`/api/events/${eventId}`);
        showMessage('Event cancelled successfully!', 'success');
        loadEvents();
    } catch (error) {
        showMessage('Error cancelling event: ' + error.message, 'error');
    }
}

// Global variable to store the event being edited
let currentEditEventId = null;

// Edit Event Functions
async function editEvent(eventId) {
    try {
        // Get event details
        const event = await apiGet(`/api/events/${eventId}`);
        
        // Store the event ID for updating
        currentEditEventId = eventId;
        
        // Populate the form with current values
        document.getElementById('edit-event-title').value = event.title || '';
        document.getElementById('edit-event-type').value = event.event_type || '';
        document.getElementById('edit-event-description').value = event.description || '';
        document.getElementById('edit-event-capacity').value = event.max_capacity || '';
        document.getElementById('edit-event-location').value = event.location || '';
        
        // Format datetime for input fields
        if (event.start_datetime) {
            const startDate = new Date(event.start_datetime);
            document.getElementById('edit-event-start').value = formatDateTimeForInput(startDate);
        }
        
        if (event.end_datetime) {
            const endDate = new Date(event.end_datetime);
            document.getElementById('edit-event-end').value = formatDateTimeForInput(endDate);
        }
        
        // Show the modal
        document.getElementById('edit-event-modal').style.display = 'block';
        
    } catch (error) {
        showMessage('Error loading event details: ' + error.message, 'error');
    }
}

async function updateEvent() {
    if (!currentEditEventId) {
        showMessage('No event selected for editing.', 'error');
        return;
    }
    
    const title = document.getElementById('edit-event-title').value.trim();
    const eventType = document.getElementById('edit-event-type').value;
    const description = document.getElementById('edit-event-description').value.trim();
    const startDateTime = document.getElementById('edit-event-start').value;
    const endDateTime = document.getElementById('edit-event-end').value;
    const maxCapacity = document.getElementById('edit-event-capacity').value;
    const location = document.getElementById('edit-event-location').value.trim();
    
    if (!title || !eventType || !startDateTime || !endDateTime) {
        showMessage('Please fill in all required fields.', 'error');
        return;
    }
    
    try {
        const eventData = {
            title,
            event_type: eventType,
            description,
            start_datetime: startDateTime,
            end_datetime: endDateTime,
            max_capacity: maxCapacity ? parseInt(maxCapacity) : null,
            location: location || null
        };
        
        await apiPut(`/api/events/${currentEditEventId}`, eventData);
        showMessage('Event updated successfully!', 'success');
        
        // Close modal and reload events
        closeModal('edit-event-modal');
        loadEvents();
        
        // Reset the edit event ID
        currentEditEventId = null;
        
    } catch (error) {
        showMessage('Error updating event: ' + error.message, 'error');
    }
}

// Helper function to format datetime for input fields
function formatDateTimeForInput(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    
    return `${year}-${month}-${day}T${hours}:${minutes}`;
}

// Note: Student registration functions removed as this functionality 
// has been moved to a separate dedicated system

function setupStarRating() {
    const stars = document.querySelectorAll('.star');
    let currentRating = 0;
    
    stars.forEach(star => {
        star.addEventListener('mouseover', function() {
            const rating = parseInt(this.dataset.rating);
            highlightStars(rating);
        });
        
        star.addEventListener('mouseout', function() {
            highlightStars(currentRating);
        });
        
        star.addEventListener('click', function() {
            currentRating = parseInt(this.dataset.rating);
            highlightStars(currentRating);
        });
    });
    
    function highlightStars(rating) {
        stars.forEach((star, index) => {
            if (index < rating) {
                star.classList.add('filled');
            } else {
                star.classList.remove('filled');
            }
        });
    }
    
    // Return current rating for external access
    return () => currentRating;
}

// Modal management functions
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        
        // Clear edit event form if closing edit modal
        if (modalId === 'edit-event-modal') {
            currentEditEventId = null;
            clearEditEventForm();
        }
    }
}

function clearEditEventForm() {
    document.getElementById('edit-event-title').value = '';
    document.getElementById('edit-event-type').value = 'hackathon';
    document.getElementById('edit-event-description').value = '';
    document.getElementById('edit-event-start').value = '';
    document.getElementById('edit-event-end').value = '';
    document.getElementById('edit-event-capacity').value = '';
    document.getElementById('edit-event-location').value = '';
}

// Setup modal close functionality
function setupModals() {
    // Setup close buttons for all modals
    document.querySelectorAll('.modal .close').forEach(closeBtn => {
        closeBtn.onclick = function() {
            const modal = this.closest('.modal');
            if (modal) {
                modal.style.display = 'none';
                
                // Clear edit form if closing edit modal
                if (modal.id === 'edit-event-modal') {
                    currentEditEventId = null;
                    clearEditEventForm();
                }
            }
        };
    });
}

// Initialize common functionality
document.addEventListener('DOMContentLoaded', function() {
    // Setup modals
    setupModals();
    
    // Close modals when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
            
            // Clear edit form if closing edit modal
            if (event.target.id === 'edit-event-modal') {
                currentEditEventId = null;
                clearEditEventForm();
            }
        }
    });
});
