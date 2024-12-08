from fastapi import FastAPI, HTTPException, Query, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
from typing import List, Optional, Dict, Any
import os
import json
import sys
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Add the FastAPI directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.append(current_dir)
sys.path.append(parent_dir)

# Import our local modules
from FastAPI.models import Feature as DBFeature
from FastAPI.automatation.database import SessionLocal, engine

# Ensure tables are created
try:
    DBFeature.__table__.create(bind=engine, checkfirst=True)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {e}")

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Karnataka Geospatial API", 
    description="API for managing Karnataka geospatial data",
    docs_url="/docs",  # OpenAPI documentation
    redoc_url="/redoc"
)

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

# Mount static files with absolute path
static_path = os.path.join(parent_dir, "static")
logger.info(f"Static files path: {static_path}")
logger.info(f"Static path exists: {os.path.exists(static_path)}")
logger.info(f"Static path contents: {os.listdir(static_path)}")
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Favicon handler
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_path = os.path.join(static_path, "favicon.ico")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    raise HTTPException(status_code=404)

# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal Server Error",
            "error": str(exc)
        }
    )

# Root endpoint to serve the main page
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # Explicitly define the index.html path
    index_path = os.path.join(static_path, "index.html")
    
    # Detailed logging
    logger.info(f"Attempting to serve index.html from: {index_path}")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Python path: {sys.path}")
    
    # Check if the file exists with absolute path
    if not os.path.exists(index_path):
        logger.error(f"Index file not found at: {index_path}")
        raise HTTPException(status_code=404, detail=f"Index file not found at {index_path}")
    
    # Serve the file
    try:
        return FileResponse(index_path)
    except Exception as e:
        logger.error(f"Error serving index.html: {e}")
        raise HTTPException(status_code=500, detail=f"Error serving index.html: {str(e)}")

# API Endpoints
@app.post("/api/features/", response_model=Dict[str, Any])
async def create_feature(feature: FeatureCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"Creating feature: {feature}")
        db_feature = DBFeature(
            name=feature.name,
            description=feature.description,
            geometry=json.dumps(feature.geometry)
        )
        db.add(db_feature)
        db.commit()
        db.refresh(db_feature)
        return {"message": "Feature created successfully", "id": db_feature.id}
    except ValidationError as ve:
        logger.error(f"Validation error: {ve}")
        raise HTTPException(status_code=422, detail=str(ve))
    except SQLAlchemyError as se:
        logger.error(f"Database error: {se}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(se))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/features/", response_model=List[Dict[str, Any]])
async def get_features(
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    try:
        features = db.query(DBFeature).offset(offset).limit(limit).all()
        return [
            {
                "id": f.id,
                "name": f.name,
                "description": f.description,
                "geometry": json.loads(f.geometry)
            }
            for f in features
        ]
    except SQLAlchemyError as se:
        logger.error(f"Database error: {se}")
        raise HTTPException(status_code=500, detail=str(se))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/features/{feature_id}", response_model=Dict[str, Any])
async def get_feature(feature_id: int, db: Session = Depends(get_db)):
    feature = db.query(DBFeature).filter(DBFeature.id == feature_id).first()
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    return {
        "id": feature.id,
        "name": feature.name,
        "description": feature.description,
        "geometry": json.loads(feature.geometry)
    }

@app.put("/api/features/{feature_id}", response_model=Dict[str, Any])
async def update_feature(
    feature_id: int,
    feature: FeatureCreate,
    db: Session = Depends(get_db)
):
    db_feature = db.query(DBFeature).filter(DBFeature.id == feature_id).first()
    if not db_feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    
    try:
        db_feature.name = feature.name
        db_feature.description = feature.description
        db_feature.geometry = json.dumps(feature.geometry)
        db.commit()
        db.refresh(db_feature)
        return {"message": "Feature updated successfully"}
    except SQLAlchemyError as se:
        logger.error(f"Database error: {se}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(se))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/features/{feature_id}")
async def delete_feature(feature_id: int, db: Session = Depends(get_db)):
    db_feature = db.query(DBFeature).filter(DBFeature.id == feature_id).first()
    if not db_feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    
    try:
        db.delete(db_feature)
        db.commit()
        return {"message": "Feature deleted successfully"}
    except SQLAlchemyError as se:
        logger.error(f"Database error: {se}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(se))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))