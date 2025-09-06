#!/usr/bin/env python3
"""
Campus Event Management Platform - Main Application Launcher
This is the entry point for the Flask application.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import the Flask app from backend
from app import app

if __name__ == '__main__':
    """
    Main entry point for the application
    Run with: python app.py
    """
    print("Starting Campus Event Management Platform...")
    print("🏫 Frontend accessible at: http://localhost:5000")
    print("📊 API endpoints available at: http://localhost:5000/api/*")
    print("🔗 Admin Portal: http://localhost:5000/admin")
    print("👨‍🎓 Student Portal: http://localhost:5000/student") 
    print("📈 Reports: http://localhost:5000/reports")
    print("=" * 60)
    
    # Run the Flask development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
