import os
import sys

# Add the FastAPI directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from automatation.database import Base

class Feature(Base):
    __tablename__ = 'features'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    geometry = Column(JSON, nullable=False)  # Store GeoJSON directly
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)