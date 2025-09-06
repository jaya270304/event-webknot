"""
Enhanced sample data for Campus Event Management Platform
Creates comprehensive test data with 4-5 colleges, 15-20 events, 30-40 students
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'database'))

from connection import execute_query, get_db_connection
from datetime import datetime, timedelta
import random

def clear_existing_data():
    """Clear all existing data for fresh start"""
    print("🧹 Clearing existing data...")
    
    queries = [
        "DELETE FROM attendance",
        "DELETE FROM registrations", 
        "DELETE FROM students",
        "DELETE FROM events",
        "DELETE FROM colleges"
    ]
    
    for query in queries:
        execute_query(query)
    
    print("✅ Existing data cleared")

def insert_colleges():
    """Insert 5 comprehensive colleges"""
    print("🏫 Inserting colleges...")
    
    colleges_data = [
        {
            'name': 'Massachusetts Institute of Technology',
            'code': 'MIT',
            'address': '77 Massachusetts Avenue',
            'city': 'Cambridge',
            'state': 'Massachusetts',
            'contact_email': 'events@mit.edu',
            'phone': '+1-617-253-1000'
        },
        {
            'name': 'Stanford University',
            'code': 'STAN',
            'address': '450 Jane Stanford Way',
            'city': 'Stanford',
            'state': 'California',
            'contact_email': 'events@stanford.edu',
            'phone': '+1-650-723-2300'
        },
        {
            'name': 'University of California Berkeley',
            'code': 'UCB',
            'address': 'Berkeley, CA 94720',
            'city': 'Berkeley',
            'state': 'California',
            'contact_email': 'events@berkeley.edu',
            'phone': '+1-510-642-6000'
        },
        {
            'name': 'Carnegie Mellon University',
            'code': 'CMU',
            'address': '5000 Forbes Avenue',
            'city': 'Pittsburgh',
            'state': 'Pennsylvania',
            'contact_email': 'events@cmu.edu',
            'phone': '+1-412-268-2000'
        },
        {
            'name': 'Georgia Institute of Technology',
            'code': 'GT',
            'address': '225 North Avenue NW',
            'city': 'Atlanta',
            'state': 'Georgia',
            'contact_email': 'events@gatech.edu',
            'phone': '+1-404-894-2000'
        }
    ]
    
    college_ids = []
    for college in colleges_data:
        query = """
            INSERT INTO colleges (name, code, address, city, state, contact_email, phone)
            VALUES (%(name)s, %(code)s, %(address)s, %(city)s, %(state)s, %(contact_email)s, %(phone)s)
            RETURNING college_id
        """
        result = execute_query(query, college, fetch='one')
        college_ids.append(result['college_id'])
        print(f"   ✓ Added {college['name']} ({college['code']})")
    
    return college_ids

def insert_students(college_ids):
    """Insert 35-40 students across all colleges"""
    print("👨‍🎓 Inserting students...")
    
    # Student names and departments
    first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'James', 'Lisa', 
                   'Robert', 'Jennifer', 'William', 'Amy', 'Richard', 'Jessica', 'Thomas',
                   'Ashley', 'Daniel', 'Amanda', 'Matthew', 'Stephanie', 'Christopher', 'Melissa',
                   'Anthony', 'Nicole', 'Mark', 'Elizabeth', 'Steven', 'Helen', 'Andrew', 'Michelle',
                   'Joshua', 'Kimberly', 'Kenneth', 'Donna', 'Kevin', 'Carol', 'Brian', 'Ruth', 'George', 'Sharon']
    
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
                  'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
                  'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson', 'White']
    
    departments = ['Computer Science', 'Electrical Engineering', 'Mechanical Engineering', 
                   'Business Administration', 'Data Science', 'Artificial Intelligence',
                   'Bioengineering', 'Chemical Engineering', 'Mathematics', 'Physics']
    
    college_codes = ['MIT', 'STAN', 'UCB', 'CMU', 'GT']
    
    student_ids = []
    student_counter = 1
    
    for i, college_id in enumerate(college_ids):
        # 7-8 students per college
        num_students = 7 if i < 3 else 8
        
        for j in range(num_students):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            name = f"{first_name} {last_name}"
            
            # Generate email
            email = f"{first_name.lower()}.{last_name.lower()}@{college_codes[i].lower()}.edu"
            
            # Generate student number
            student_number = f"{college_codes[i]}{str(student_counter).zfill(3)}"
            
            # Generate phone
            phone = f"+1-{random.randint(200,999)}-{random.randint(200,999)}-{random.randint(1000,9999)}"
            
            student_data = {
                'college_id': college_id,
                'email': email,
                'name': name,
                'student_number': student_number,
                'phone': phone,
                'year_of_study': random.randint(1, 4),
                'department': random.choice(departments)
            }
            
            query = """
                INSERT INTO students (college_id, email, name, student_number, phone, year_of_study, department)
                VALUES (%(college_id)s, %(email)s, %(name)s, %(student_number)s, %(phone)s, %(year_of_study)s, %(department)s)
                RETURNING student_id
            """
            
            result = execute_query(query, student_data, fetch='one')
            student_ids.append(result['student_id'])
            student_counter += 1
            
    print(f"   ✓ Added {len(student_ids)} students across all colleges")
    return student_ids

def insert_events(college_ids):
    """Insert 18-20 diverse events"""
    print("🎯 Inserting events...")
    
    base_date = datetime.now() + timedelta(days=5)
    
    events_data = [
        # MIT Events
        {
            'college_id': college_ids[0],
            'title': 'MIT AI/ML Workshop Series',
            'description': 'Comprehensive workshop series covering machine learning fundamentals, deep learning, and practical AI applications',
            'event_type': 'workshop',
            'start_datetime': base_date + timedelta(days=7),
            'end_datetime': base_date + timedelta(days=7, hours=8),
            'location': 'MIT Stata Center, Building 32',
            'max_capacity': 60,
            'created_by': 'MIT Events Team'
        },
        {
            'college_id': college_ids[0],
            'title': 'MIT Innovation Hackathon 2025',
            'description': '48-hour hackathon focusing on sustainable technology and climate solutions',
            'event_type': 'hackathon',
            'start_datetime': base_date + timedelta(days=14),
            'end_datetime': base_date + timedelta(days=16),
            'location': 'MIT Student Center',
            'max_capacity': 120,
            'created_by': 'MIT Hackathon Club'
        },
        {
            'college_id': college_ids[0],
            'title': 'Tech Giants Career Talk',
            'description': 'Industry leaders from Google, Apple, and Microsoft share career insights',
            'event_type': 'tech_talk',
            'start_datetime': base_date + timedelta(days=21),
            'end_datetime': base_date + timedelta(days=21, hours=3),
            'location': 'MIT Kresge Auditorium',
            'max_capacity': 300,
            'created_by': 'MIT Career Services'
        },
        
        # Stanford Events  
        {
            'college_id': college_ids[1],
            'title': 'Stanford Entrepreneurship Fest',
            'description': 'Three-day festival celebrating innovation, startups, and entrepreneurial spirit',
            'event_type': 'fest',
            'start_datetime': base_date + timedelta(days=28),
            'end_datetime': base_date + timedelta(days=30),
            'location': 'Stanford Memorial Auditorium',
            'max_capacity': 500,
            'created_by': 'Stanford Entrepreneurship Program'
        },
        {
            'college_id': college_ids[1],
            'title': 'Blockchain and Web3 Workshop',
            'description': 'Hands-on workshop covering blockchain technology, smart contracts, and DeFi',
            'event_type': 'workshop',
            'start_datetime': base_date + timedelta(days=35),
            'end_datetime': base_date + timedelta(days=35, hours=6),
            'location': 'Stanford Gates Building',
            'max_capacity': 45,
            'created_by': 'Stanford Blockchain Club'
        },
        {
            'college_id': college_ids[1],
            'title': 'Future of Computing Symposium',
            'description': 'Expert panel discussion on quantum computing, edge computing, and AI acceleration',
            'event_type': 'tech_talk',
            'start_datetime': base_date + timedelta(days=42),
            'end_datetime': base_date + timedelta(days=42, hours=4),
            'location': 'Stanford Memorial Church',
            'max_capacity': 250,
            'created_by': 'Stanford CS Department'
        },
        
        # UC Berkeley Events
        {
            'college_id': college_ids[2],
            'title': 'Cal Hacks: Social Impact Edition',
            'description': '36-hour hackathon focused on technology solutions for social good',
            'event_type': 'hackathon',
            'start_datetime': base_date + timedelta(days=49),
            'end_datetime': base_date + timedelta(days=50, hours=12),
            'location': 'UC Berkeley RSF',
            'max_capacity': 200,
            'created_by': 'Cal Hacks Team'
        },
        {
            'college_id': college_ids[2],
            'title': 'Data Science Bootcamp',
            'description': 'Intensive bootcamp covering Python, R, machine learning, and data visualization',
            'event_type': 'workshop',
            'start_datetime': base_date + timedelta(days=56),
            'end_datetime': base_date + timedelta(days=58),
            'location': 'UC Berkeley Soda Hall',
            'max_capacity': 80,
            'created_by': 'Berkeley Data Science Society'
        },
        {
            'college_id': college_ids[2],
            'title': 'Berkeley Tech Symposium',
            'description': 'Annual technology conference featuring industry leaders and researchers',
            'event_type': 'fest',
            'start_datetime': base_date + timedelta(days=63),
            'end_datetime': base_date + timedelta(days=64),
            'location': 'UC Berkeley Zellerbach Hall',
            'max_capacity': 400,
            'created_by': 'Berkeley Tech Society'
        },
        {
            'college_id': college_ids[2],
            'title': 'Cybersecurity Workshop Series',
            'description': 'Multi-session workshop on network security, ethical hacking, and privacy',
            'event_type': 'workshop',
            'start_datetime': base_date + timedelta(days=70),
            'end_datetime': base_date + timedelta(days=70, hours=5),
            'location': 'UC Berkeley Cory Hall',
            'max_capacity': 35,
            'created_by': 'Berkeley Security Club'
        },
        
        # Carnegie Mellon Events
        {
            'college_id': college_ids[3],
            'title': 'CMU Robotics Competition',
            'description': 'Annual robotics design and programming competition with industry judges',
            'event_type': 'hackathon',
            'start_datetime': base_date + timedelta(days=77),
            'end_datetime': base_date + timedelta(days=78),
            'location': 'CMU Newell-Simon Hall',
            'max_capacity': 100,
            'created_by': 'CMU Robotics Institute'
        },
        {
            'college_id': college_ids[3],
            'title': 'Human-Computer Interaction Workshop',
            'description': 'Workshop on UX design, user research, and interaction design principles',
            'event_type': 'workshop',
            'start_datetime': base_date + timedelta(days=84),
            'end_datetime': base_date + timedelta(days=84, hours=7),
            'location': 'CMU Hunt Library',
            'max_capacity': 50,
            'created_by': 'CMU HCI Institute'
        },
        {
            'college_id': college_ids[3],
            'title': 'Tech Industry Career Panel',
            'description': 'Panel discussion with CMU alumni working at top tech companies',
            'event_type': 'tech_talk',
            'start_datetime': base_date + timedelta(days=91),
            'end_datetime': base_date + timedelta(days=91, hours=2),
            'location': 'CMU McConomy Auditorium',
            'max_capacity': 200,
            'created_by': 'CMU Career Services'
        },
        
        # Georgia Tech Events
        {
            'college_id': college_ids[4],
            'title': 'HackGT: Health Tech Challenge',
            'description': '24-hour hackathon focusing on healthcare technology and medical innovations',
            'event_type': 'hackathon',
            'start_datetime': base_date + timedelta(days=98),
            'end_datetime': base_date + timedelta(days=99),
            'location': 'Georgia Tech Student Center',
            'max_capacity': 150,
            'created_by': 'HackGT Team'
        },
        {
            'college_id': college_ids[4],
            'title': 'GT Innovation Showcase',
            'description': 'Two-day showcase of student projects, research, and startup presentations',
            'event_type': 'fest',
            'start_datetime': base_date + timedelta(days=105),
            'end_datetime': base_date + timedelta(days=106),
            'location': 'Georgia Tech Campus Recreation Center',
            'max_capacity': 600,
            'created_by': 'GT Innovation Program'
        },
        {
            'college_id': college_ids[4],
            'title': 'Cloud Computing Workshop',
            'description': 'Comprehensive workshop on AWS, Azure, and Google Cloud Platform',
            'event_type': 'workshop',
            'start_datetime': base_date + timedelta(days=112),
            'end_datetime': base_date + timedelta(days=112, hours=6),
            'location': 'Georgia Tech Klaus Building',
            'max_capacity': 70,
            'created_by': 'GT Cloud Computing Club'
        },
        {
            'college_id': college_ids[4],
            'title': 'Tech Leadership Summit',
            'description': 'Leadership development program for aspiring tech leaders and managers',
            'event_type': 'tech_talk',
            'start_datetime': base_date + timedelta(days=119),
            'end_datetime': base_date + timedelta(days=119, hours=5),
            'location': 'Georgia Tech Scheller College',
            'max_capacity': 120,
            'created_by': 'GT Leadership Program'
        },
        
        # Cross-college collaborative events
        {
            'college_id': college_ids[0],  # Hosted by MIT
            'title': 'Inter-University AI Summit',
            'description': 'Collaborative summit bringing together AI researchers and students from top universities',
            'event_type': 'fest',
            'start_datetime': base_date + timedelta(days=126),
            'end_datetime': base_date + timedelta(days=127),
            'location': 'MIT Media Lab',
            'max_capacity': 300,
            'created_by': 'Inter-University AI Consortium'
        },
        {
            'college_id': college_ids[1],  # Hosted by Stanford
            'title': 'Global Tech Ethics Workshop',
            'description': 'Multi-university workshop on technology ethics, privacy, and social responsibility',
            'event_type': 'workshop',
            'start_datetime': base_date + timedelta(days=133),
            'end_datetime': base_date + timedelta(days=133, hours=8),
            'location': 'Stanford d.school',
            'max_capacity': 100,
            'created_by': 'Tech Ethics Coalition'
        }
    ]
    
    event_ids = []
    for i, event in enumerate(events_data):
        query = """
            INSERT INTO events (college_id, title, description, event_type, start_datetime, 
                              end_datetime, location, max_capacity, created_by)
            VALUES (%(college_id)s, %(title)s, %(description)s, %(event_type)s, %(start_datetime)s,
                   %(end_datetime)s, %(location)s, %(max_capacity)s, %(created_by)s)
            RETURNING event_id
        """
        
        result = execute_query(query, event, fetch='one')
        event_ids.append(result['event_id'])
        
    print(f"   ✓ Added {len(event_ids)} events across all colleges")
    return event_ids

def insert_registrations(student_ids, event_ids):
    """Insert realistic registrations with some students in multiple events"""
    print("📝 Inserting registrations...")
    
    registration_ids = []
    
    # Strategy: Each event gets 30-80% capacity registrations
    for event_id in event_ids:
        # Get event capacity
        query = "SELECT max_capacity FROM events WHERE event_id = %s"
        result = execute_query(query, (event_id,), fetch='one')
        max_capacity = result['max_capacity']
        
        # Calculate number of registrations (30-80% of capacity)
        if max_capacity:
            num_registrations = random.randint(
                max(1, int(max_capacity * 0.3)), 
                int(max_capacity * 0.8)
            )
        else:
            num_registrations = random.randint(15, 25)  # For unlimited events
        
        # Randomly select students for this event
        selected_students = random.sample(student_ids, min(num_registrations, len(student_ids)))
        
        for student_id in selected_students:
            try:
                registration_data = {
                    'event_id': event_id,
                    'student_id': student_id,
                    'status': random.choices(['registered', 'cancelled'], weights=[90, 10])[0]
                }
                
                query = """
                    INSERT INTO registrations (event_id, student_id, status)
                    VALUES (%(event_id)s, %(student_id)s, %(status)s)
                    RETURNING registration_id
                """
                
                result = execute_query(query, registration_data, fetch='one')
                registration_ids.append(result['registration_id'])
                
            except Exception as e:
                # Skip duplicate registrations
                continue
    
    print(f"   ✓ Added {len(registration_ids)} registrations")
    return registration_ids

def insert_attendance_and_feedback(registration_ids):
    """Insert attendance records with realistic feedback patterns"""
    print("✅ Inserting attendance and feedback...")
    
    # 60-85% of registered students actually attend
    num_attending = int(len(registration_ids) * random.uniform(0.6, 0.85))
    attending_registrations = random.sample(registration_ids, num_attending)
    
    attendance_count = 0
    feedback_count = 0
    
    for registration_id in attending_registrations:
        # Create attendance record
        attendance_data = {
            'registration_id': registration_id,
            'check_in_method': random.choices(
                ['manual', 'qr_code', 'rfid'], 
                weights=[60, 30, 10]
            )[0]
        }
        
        query = """
            INSERT INTO attendance (registration_id, check_in_method)
            VALUES (%(registration_id)s, %(check_in_method)s)
            RETURNING attendance_id
        """
        
        result = execute_query(query, attendance_data, fetch='one')
        attendance_count += 1
        
        # 70% of attendees provide feedback
        if random.random() < 0.7:
            feedback_data = {
                'attendance_id': result['attendance_id'],
                'rating': random.choices([1, 2, 3, 4, 5], weights=[2, 5, 15, 35, 43])[0],  # Skewed positive
                'comment': random.choice([
                    'Excellent event! Very informative and well organized.',
                    'Great workshop with practical examples and hands-on exercises.',
                    'Good content but could use better time management.',
                    'Amazing speakers and networking opportunities.',
                    'Highly recommend this event to other students.',
                    'Well structured content with clear takeaways.',
                    'Could benefit from more interactive sessions.',
                    'Fantastic event! Learned a lot and made great connections.',
                    'Good event overall, met my expectations.',
                    'Excellent organization and venue selection.',
                    None, None  # Some without comments
                ])
            }
            
            query = """
                UPDATE attendance 
                SET feedback_rating = %(rating)s, 
                    feedback_comment = %(comment)s,
                    feedback_submitted_at = CURRENT_TIMESTAMP
                WHERE attendance_id = %(attendance_id)s
            """
            
            execute_query(query, feedback_data)
            feedback_count += 1
    
    print(f"   ✓ Added {attendance_count} attendance records")
    print(f"   ✓ Added {feedback_count} feedback submissions")

def generate_sample_data():
    """Main function to generate all sample data"""
    print("🚀 Starting enhanced sample data generation...")
    print("=" * 60)
    
    try:
        # Clear existing data
        clear_existing_data()
        
        # Insert data in order
        college_ids = insert_colleges()
        student_ids = insert_students(college_ids) 
        event_ids = insert_events(college_ids)
        registration_ids = insert_registrations(student_ids, event_ids)
        insert_attendance_and_feedback(registration_ids)
        
        print("=" * 60)
        print("✅ Enhanced sample data generation completed successfully!")
        print("\n📊 Summary:")
        print(f"   🏫 Colleges: {len(college_ids)}")
        print(f"   👨‍🎓 Students: {len(student_ids)}")
        print(f"   🎯 Events: {len(event_ids)}")
        print(f"   📝 Registrations: {len(registration_ids)}")
        print("\n🎉 Database is ready for testing!")
        
    except Exception as e:
        print(f"❌ Error during data generation: {e}")
        return False
        
    return True

if __name__ == "__main__":
    success = generate_sample_data()
    if not success:
        exit(1)
