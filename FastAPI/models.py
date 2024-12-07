from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from .automatation.database import Base  # Changed to relative import

class Feature(Base):
    __tablename__ = 'features'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    geometry = Column(JSON, nullable=False)  # Store GeoJSON directly
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)