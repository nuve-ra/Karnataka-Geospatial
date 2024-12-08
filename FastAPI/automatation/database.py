from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
import os
from dotenv import load_dotenv
from typing import List

# Load environment variables from .env file
load_dotenv()

# Database connection parameters
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgis_35")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Mymobile11")

# SQLAlchemy Database URL (using pg8000)
SQLALCHEMY_DATABASE_URL = f"postgresql+pg8000://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for SQLAlchemy models
Base = declarative_base()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define the Feature model
class Feature(Base):
    __tablename__ = 'features'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, default="No description")
    geometry = Column(String)  # GeoJSON as string for simplicity

# Create the database tables (This should only be run once to create the schema)
Base.metadata.create_all(bind=engine)

# FastAPI app setup
app = FastAPI()

# Endpoint to get all features
@app.get("/api/features/", response_model=List[dict])
def get_features(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    try:
        # Query the database
        features = db.query(Feature).offset(offset).limit(limit).all()
        if not features:
            raise HTTPException(status_code=404, detail="No features found")
        return features
    except SQLAlchemyError as e:
        print(f"SQLAlchemy error: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        print(f"General error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Endpoint to create or update a feature
@app.post("/api/features/")
def create_feature(feature: dict, db: Session = Depends(get_db)):
    try:
        new_feature = Feature(
            name=feature["name"],
            description=feature.get("description", "No description"),
            geometry=feature["geometry"]
        )
        db.add(new_feature)
        db.commit()
        db.refresh(new_feature)
        return new_feature
    except SQLAlchemyError as e:
        print(f"SQLAlchemy error: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        print(f"General error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Endpoint to delete a feature
@app.delete("/api/features/{feature_id}")
def delete_feature(feature_id: int, db: Session = Depends(get_db)):
    try:
        feature = db.query(Feature).filter(Feature.id == feature_id).first()
        if not feature:
            raise HTTPException(status_code=404, detail="Feature not found")
        
        db.delete(feature)
        db.commit()
        return {"message": "Feature deleted successfully"}
    except SQLAlchemyError as e:
        print(f"SQLAlchemy error: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        print(f"General error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
