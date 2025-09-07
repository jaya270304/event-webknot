# Campus Event Management System

## Implementation Video

[![Implemetation Video](https://img.youtube.com/vi/Y31_XN0VEqI/0.jpg)](https://youtu.be/Y31_XN0VEqI)

## My Understanding of This Project

I used Flask for the backend because it's simple ,just Python handling endpoinst and talking to a PostgreSQL database. The frontend is just HTML, CSS, and JavaScript to keep it simple. I made five database tables that link together properly : colleges, events, students, registrations, and attendance , so when you delete a college, everything related gets cleaned up automatically. The whole thing runs on one server, handles about 25,000 students across 50 colleges, and gives you real-time reports without any complicated setup.

## What This Thing Actually Does

There are two kinds of users of this:

1. **Admins** - They can create events, view registered users, mark attendance, and generate reports
2. **Students** - They can view events, register for events, and provide feedback after attending

## What is actually in this repo ?

1)First is the backend dir which has app.py , this has all the endpointns.
2)The bonus dir which has all the sql commands which the file's name itself depicts.
3)Next is the database dir , this is what connects with the database and also has the schema for the db.
4)Then is the database_screenshots which has the screenshots of the populated db on my local pc.
5)The Documents directory has literally everything , from the api documentation to all the required documents.
6)Next is the sample-data directory which has the data to populate your db in case if you decide to host it.
7)The static dir has the css and js for the entire project.
8)The templates directory has the html files which are the templates file for the project.
9)THe user_flow_screenshots has the proper user flow of how an admin/student goes through the applciation , the "campus-event-management\Documents\User-Flow-Documentation.pdf" has an extremely clear depiction of what the user flow is with detailed explanation.

## Technical Stuff I Used

It's Simple:
- **Backend**: Python Flask (since I am proficient in Python)
- **Database**: PostgreSQL (since it is more stable than SQLite for multiple colleges)
- **Frontend**: HTML, CSS, JavaScript (no frameworks)
I ensure it works with older python versions also ...

## How I Set Up The Database

I created 5 primary tables:
- **colleges**: Save college data such as name and code
- **events**: Save all the event data such as title, date, description
- **students**: Student data along with their college
- **registrations**: Who registered for which event
- **attendance**: Who actually attended and their ratings

I linked them accordingly so if you remove a college, all its events also get removed. Simple things but necessary.

## Backend Logic

Flask backend takes care of:
- Validating if data is valid before saving
- Developing APIs for frontend to consume
- Creating reports using SQL queries

I broke the code into separate files so it's clean.

## How To Run This On Your Computer

You require:
- Python 3.7 or later
- PostgreSQL database

### Setup for Database

1. Install PostgreSQL and create a database named campus_events
2. Open the file database/connection.py and insert your database credentials:
   python
   DB_HOST = 'localhost'
   DB_NAME = 'campus_events'
   DB_USER = 'your_username'
   DB_PASSWORD = 'your_password'
   

### Installation and Running

1. Install the following required Python packages:

pip install -r requirements.txt


2. Initialize the database tables:

python -c "from database.connection import init_database; init_database()"


3. Populate some sample data to play with:

python sample-data/seed_enhanced_data.py


4. Run the website:

python app.py


Then launch your web browser and navigate to:
- Main page: http://localhost:5000
- Admin side: http://localhost:5000/admin
- Student side: http://localhost:5000/student
- Reports page: http://localhost:5000/reports

## Why I Built It This Way

I did not want to make it too complicated but useful. No parts that get damaged easily. Just good solid code that gets the job done and addresses actual issues. The assignment was to think practically, so I centered around what actually college staff and students require on a daily basis.

This does a good job with the general event lifecycle - create, register, attend, feedback, analyze. That handles like 90% of what most universities require of event management.



