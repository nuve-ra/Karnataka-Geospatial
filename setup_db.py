import os
import sys

# Add the FastAPI directory to the Python path
fastapi_dir = os.path.join(os.path.dirname(__file__), 'FastAPI')
sys.path.append(fastapi_dir)

# Now import and run the database initialization
from init_db import init_db

if __name__ == "__main__":
    init_db()
