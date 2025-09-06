// Reports and Analytics JavaScript Functions

// Load colleges for reports
async function loadCollegesForReports() {
    try {
        const colleges = await apiGet('/api/colleges');
        const dropdown = document.getElementById('report-college');
        
        if (dropdown && colleges.length > 0) {
            // Keep "All Colleges" option
            const allOption = dropdown.querySelector('option').outerHTML;
            dropdown.innerHTML = allOption + colleges.map(college => 
                `<option value="${college.college_id}">${college.name} (${college.code})</option>`
            ).join('');
        }
        
        // Also populate events dropdown when college is selected
        const collegeDropdown = document.getElementById('report-college');
        collegeDropdown.addEventListener('change', loadEventsForReports);
        
    } catch (error) {
        console.error('Error loading colleges for reports:', error);
    }
}

async function loadEventsForReports() {
    const collegeId = document.getElementById('report-college').value;
    const eventDropdown = document.getElementById('report-event');
    
    try {
        if (collegeId) {
            const events = await apiGet(`/api/colleges/${collegeId}/events`);
            eventDropdown.innerHTML = '<option value="">All Events</option>' + 
                events.map(event => 
                    `<option value="${event.event_id}">${event.title} (${formatDate(event.start_datetime)})</option>`
                ).join('');
        } else {
            eventDropdown.innerHTML = '<option value="">All Events</option>';
        }
    } catch (error) {
        console.error('Error loading events for reports:', error);
        eventDropdown.innerHTML = '<option value="">All Events</option>';
    }
}

// System overview functions
async function loadSystemOverview() {
    try {
        const overview = await apiGet('/api/reports/system-overview');
        
        // Update overview stats with real data
        document.getElementById('overview-colleges').textContent = overview.total_colleges || 0;
        document.getElementById('overview-events').textContent = overview.total_active_events || 0;
        document.getElementById('overview-registrations').textContent = overview.total_active_registrations || 0;
        document.getElementById('overview-attendance-rate').textContent = (overview.overall_avg_rating ? overview.overall_avg_rating + '⭐' : 'N/A');
        
        showMessage('System overview loaded successfully!', 'success');
        
    } catch (error) {
        console.error('Error loading system overview:', error);
        showMessage('Error loading system overview: ' + error.message, 'error');
        // Set default values on error
        document.getElementById('overview-colleges').textContent = '0';
        document.getElementById('overview-events').textContent = '0';
        document.getElementById('overview-registrations').textContent = '0';
        document.getElementById('overview-attendance-rate').textContent = '0';
    }
}

// Generate college report
async function generateCollegeReport() {
    const collegeId = document.getElementById('report-college').value;
    
    if (!collegeId) {
        showMessage('Please select a college to generate report.', 'error');
        return;
    }
    
    try {
        const events = await apiGet(`/api/reports/filter?college_id=${collegeId}&type=events`);
        
        const container = document.getElementById('events-report');
        
        if (events.length === 0) {
            container.innerHTML = '<div class="message info">No events found for the selected college.</div>';
            return;
        }
        
        container.innerHTML = `
            <h3>📊 College Event Performance Report</h3>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Event Name</th>
                            <th>Type</th>
                            <th>Date</th>
                            <th>Registrations</th>
                            <th>Attendance</th>
                            <th>Attendance %</th>
                            <th>Avg Rating</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${events.map(event => `
                            <tr>
                                <td><strong>${event.event_name}</strong></td>
                                <td><span class="event-type ${event.event_type}">${event.event_type.replace('_', ' ').toUpperCase()}</span></td>
                                <td>${formatDateTime(event.start_datetime)}</td>
                                <td>${event.registrations}</td>
                                <td>${event.attendance}</td>
                                <td>
                                    <strong style="color: ${event.attendance_percentage >= 80 ? '#28a745' : event.attendance_percentage >= 60 ? '#ffc107' : '#dc3545'}">
                                        ${event.attendance_percentage}%
                                    </strong>
                                </td>
                                <td>${event.avg_rating ? event.avg_rating + ' ⭐' : 'N/A'}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        showMessage('College report generated successfully!', 'success');
        
    } catch (error) {
        showMessage('Error generating college report: ' + error.message, 'error');
    }
}

// Generate individual event report
async function generateEventReport() {
    const eventId = document.getElementById('report-event').value;
    
    if (!eventId) {
        showMessage('Please select an event to generate detailed report.', 'error');
        return;
    }
    
    try {
        const stats = await apiGet(`/api/events/${eventId}/stats`);
        
        const section = document.getElementById('event-details-section');
        const container = document.getElementById('event-stats');
        
        container.innerHTML = `
            <h3>📊 ${stats.title} - Detailed Analysis</h3>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">${stats.total_registrations}</div>
                    <div class="stat-label">Total Registrations</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.active_registrations}</div>
                    <div class="stat-label">Active Registrations</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.total_attendance}</div>
                    <div class="stat-label">Attendees</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.attendance_percentage}%</div>
                    <div class="stat-label">Attendance Rate</div>
                </div>
            </div>
            
            <div class="card-grid">
                <div class="card">
                    <h4>📈 Performance Metrics</h4>
                    <p><strong>Event Type:</strong> ${stats.event_type.replace('_', ' ').toUpperCase()}</p>
                    <p><strong>Duration:</strong> ${formatDateTime(stats.start_datetime)} - ${formatDateTime(stats.end_datetime)}</p>
                    <p><strong>Attendance Rate:</strong> 
                        <span style="color: ${stats.attendance_percentage >= 80 ? '#28a745' : stats.attendance_percentage >= 60 ? '#ffc107' : '#dc3545'}">
                            ${stats.attendance_percentage}%
                        </span>
                    </p>
                </div>
                
                <div class="card">
                    <h4>⭐ Feedback Analysis</h4>
                    <p><strong>Average Rating:</strong> ${stats.avg_rating ? stats.avg_rating + ' ⭐' : 'No ratings yet'}</p>
                    <p><strong>Total Feedback:</strong> ${stats.feedback_count} submissions</p>
                    <p><strong>Response Rate:</strong> 
                        ${stats.total_attendance > 0 ? 
                            Math.round((stats.feedback_count / stats.total_attendance) * 100) + '%' : 
                            'N/A'
                        }
                    </p>
                </div>
            </div>
        `;
        
        section.style.display = 'block';
        showMessage('Event report generated successfully!', 'success');
        
    } catch (error) {
        showMessage('Error generating event report: ' + error.message, 'error');
    }
}

// Load top performing events
async function loadTopEvents() {
    try {
        const events = await apiGet('/api/reports/event-popularity');
        
        const tableBody = document.getElementById('top-events-table');
        
        if (events.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="7" class="loading">No events data available</td></tr>';
            return;
        }
        
        // Take top 10 events
        const topEvents = events.slice(0, 10);
        
        tableBody.innerHTML = topEvents.map(event => `
            <tr>
                <td><strong>${event.event_name}</strong></td>
                <td><span class="event-type ${event.event_type}">${event.event_type.replace('_', ' ').toUpperCase()}</span></td>
                <td>${event.college_name}</td>
                <td>${event.total_registrations}</td>
                <td>${event.active_registrations}</td>
                <td>
                    <strong style="color: ${event.capacity_utilization === 'Full' ? '#28a745' : '#ffc107'}">${event.capacity_utilization}</strong>
                </td>
                <td>${event.registration_status}</td>
            </tr>
        `).join('');
        
    } catch (error) {
        console.error('Error loading top events:', error);
        document.getElementById('top-events-table').innerHTML = 
            '<tr><td colspan="7" class="loading">Error loading top events: ' + error.message + '</td></tr>';
    }
}

// Load college comparison data
async function loadCollegeComparison() {
    try {
        const colleges = await apiGet('/api/reports/college-performance');
        
        const tableBody = document.getElementById('college-comparison-table');
        
        if (colleges.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="6" class="loading">No college data available</td></tr>';
            return;
        }
        
        tableBody.innerHTML = colleges.map(college => `
            <tr>
                <td><strong>${college.college_name}</strong></td>
                <td>${college.total_events}</td>
                <td>${college.total_registrations}</td>
                <td>${college.total_attendance}</td>
                <td>
                    <strong style="color: ${college.attendance_percentage >= 85 ? '#28a745' : college.attendance_percentage >= 60 ? '#ffc107' : '#dc3545'}">
                        ${college.attendance_percentage}%
                    </strong>
                </td>
                <td>${college.avg_feedback_rating ? college.avg_feedback_rating + ' ⭐' : 'N/A'}</td>
            </tr>
        `).join('');
        
    } catch (error) {
        console.error('Error loading college comparison:', error);
        document.getElementById('college-comparison-table').innerHTML = 
            '<tr><td colspan="6" class="loading">Error loading college data: ' + error.message + '</td></tr>';
    }
}

// Load event type statistics
async function loadEventTypeStats() {
    try {
        const typeStats = await apiGet('/api/reports/event-type-analytics');
        
        // Initialize counts
        const typeCounts = {
            hackathon: 0,
            workshop: 0,
            tech_talk: 0,
            fest: 0
        };
        
        // Count events by type from analytics
        typeStats.forEach(stat => {
            typeCounts[stat.event_type] = stat.total_events;
        });
        
        // Update stat cards
        document.getElementById('hackathon-count').textContent = typeCounts.hackathon;
        document.getElementById('workshop-count').textContent = typeCounts.workshop;
        document.getElementById('tech-talk-count').textContent = typeCounts.tech_talk;
        document.getElementById('fest-count').textContent = typeCounts.fest;
        
    } catch (error) {
        console.error('Error loading event type stats:', error);
        // Set default values on error
        document.getElementById('hackathon-count').textContent = '0';
        document.getElementById('workshop-count').textContent = '0';
        document.getElementById('tech-talk-count').textContent = '0';
        document.getElementById('fest-count').textContent = '0';
    }
}
