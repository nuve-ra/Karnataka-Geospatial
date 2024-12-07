from fastapi import FastAPI, HTTPException, Query, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json

# Import our local modules using relative imports
from .models import Feature as DBFeature
from .automatation.database import SessionLocal

# Load environment variables
load_dotenv()


# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(title="Geospatial API", description="API for managing geospatial data")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for feature creation
class FeatureCreate(BaseModel):
    name: str
    description: Optional[str] = None
    geometry: Dict[str, Any]  # GeoJSON geometry

# Templates setup with absolute path
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"))

# Mount static files with absolute path
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")), name="static")

# Get database session
def get_db():
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()

# Use it in endpoints like this:
@app.post("/api/features")
async def create_feature(feature: FeatureCreate, db_session: Session = Depends(get_db)):
    try:
        db_feature = DBFeature(
            name=feature.name,
            description=feature.description,
            geometry=feature.geometry
        )
        db_session.add(db_feature)
        db_session.commit()
        db_session.refresh(db_feature)
        return db_feature
    except Exception as e:
        print(f"Error creating feature: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/features")
async def get_features(
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get all features with pagination"""
    try:
        db = next(get_db())
        features = db.query(DBFeature).offset(offset).limit(limit).all()
        return features
    except Exception as e:
        print(f"Error getting features: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/features/{feature_id}")
async def get_feature(feature_id: int):
    """Get a specific feature by ID"""
    try:
        db = next(get_db())
        feature = db.query(DBFeature).filter(DBFeature.id == feature_id).first()
        if feature is None:
            raise HTTPException(status_code=404, detail="Feature not found")
        return feature
    except Exception as e:
        print(f"Error getting feature: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/features/{feature_id}")
async def update_feature(feature_id: int, feature: FeatureCreate):
    """Update an existing feature"""
    try:
        db = next(get_db())
        db_feature = db.query(DBFeature).filter(DBFeature.id == feature_id).first()
        if db_feature is None:
            raise HTTPException(status_code=404, detail="Feature not found")
        
        db_feature.name = feature.name
        db_feature.description = feature.description
        db_feature.geometry = feature.geometry
        
        db.commit()
        db.refresh(db_feature)
        return db_feature
    except Exception as e:
        print(f"Error updating feature: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/features/{feature_id}")
async def delete_feature(feature_id: int):
    """Delete a feature"""
    try:
        db = next(get_db())
        feature = db.query(DBFeature).filter(DBFeature.id == feature_id).first()
        if feature is None:
            raise HTTPException(status_code=404, detail="Feature not found")
        
        db.delete(feature)
        db.commit()
        return {"message": "Feature deleted successfully"}
    except Exception as e:
        print(f"Error deleting feature: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))