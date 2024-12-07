# What is this project?

This is a web application that helps you store and manage location-based data (like points on a map). You can add, view, update, and delete locations using either our web interface or our API.

# What do I need to run it?

- Python 3.11
- PostgreSQL database with PostGIS (for storing location data)
- A few Python packages (listed in requirements.txt)

# How do I set it up?

1. First time setup:
   - Install Python 3.11 from python.org
   - Install PostgreSQL and PostGIS
   - Create a database called 'postgis_35'

2.Open the project in browser
   - open terminal
   - cd to the project directory
   - Start the server:uvicorn FastAPI.api:app --reload
   - Open http://localhost:8000 in your browser
   - Open http://127.0.0.1:8000/docs to access the API documentation
   - Open http://127.0.0.1:8000/redoc for frontend
    
3. Set up your database connection:
   Create a file called `.env` with your database details: