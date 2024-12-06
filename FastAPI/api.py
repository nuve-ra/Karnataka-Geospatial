from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Optional
import os
import geojson
from shapely.geometry import shape
import geopandas as gpd
from geoalchemy2.shape import to_shape
import json

# Load environment variables
load_dotenv()

app = FastAPI(title="Geospatial API", description="API for managing geospatial data")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Database connection
def get_db_engine():
    db_params = {
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD')
    }
    connection_string = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
    return create_engine(connection_string)

# Pydantic models for request/response
class GeometryBase(BaseModel):
    type: str
    coordinates: List

class FeatureProperties(BaseModel):
    name: str
    description: Optional[str] = None

class Feature(BaseModel):
    type: str = "Feature"
    geometry: GeometryBase
    properties: FeatureProperties

# API endpoints
@app.get("/", response_class=HTMLResponse)
async def frontend(request: Request):
    """Serve the frontend HTML page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api")
async def root():
    """API root endpoint"""
    return {"message": "Welcome to the Geospatial API"}

@app.get("/api/features")
async def get_features(
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get all features with pagination"""
    try:
        engine = get_db_engine()
        with engine.connect() as connection:
            query = text("""
                SELECT json_build_object(
                    'type', 'FeatureCollection',
                    'features', json_agg(
                        json_build_object(
                            'type', 'Feature',
                            'id', gid,
                            'geometry', ST_AsGeoJSON(geometry)::json,
                            'properties', json_build_object(
                                'name', name
                            )
                        )
                    )
                )
                FROM (
                    SELECT gid, geometry, name
                    FROM countries
                    LIMIT :limit OFFSET :offset
                ) AS features;
            """)
            result = connection.execute(query, {"limit": limit, "offset": offset}).scalar()
            return result if result else {"type": "FeatureCollection", "features": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/features/{feature_id}")
async def get_feature(feature_id: int):
    """Get a specific feature by ID"""
    try:
        engine = get_db_engine()
        with engine.connect() as connection:
            query = text("""
                SELECT json_build_object(
                    'type', 'Feature',
                    'id', gid,
                    'geometry', ST_AsGeoJSON(geometry)::json,
                    'properties', json_build_object(
                        'name', name
                    )
                )
                FROM countries
                WHERE gid = :feature_id;
            """)
            result = connection.execute(query, {"feature_id": feature_id}).scalar()
            if not result:
                raise HTTPException(status_code=404, detail="Feature not found")
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/features")
async def create_feature(feature: Feature):
    """Create a new feature"""
    try:
        engine = get_db_engine()
        with engine.connect() as connection:
            # Convert GeoJSON geometry to WKT
            geom = shape(feature.geometry.dict())
            query = text("""
                INSERT INTO countries (geometry, name)
                VALUES (ST_SetSRID(ST_GeomFromText(:wkt), 4326), :name)
                RETURNING gid;
            """)
            result = connection.execute(
                query,
                {
                    "wkt": geom.wkt,
                    "name": feature.properties.name
                }
            ).scalar()
            return {"id": result, "message": "Feature created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/features/{feature_id}")
async def update_feature(feature_id: int, feature: Feature):
    """Update an existing feature"""
    try:
        engine = get_db_engine()
        with engine.connect() as connection:
            # Convert GeoJSON geometry to WKT
            geom = shape(feature.geometry.dict())
            query = text("""
                UPDATE countries
                SET geometry = ST_SetSRID(ST_GeomFromText(:wkt), 4326),
                    name = :name
                WHERE gid = :feature_id
                RETURNING gid;
            """)
            result = connection.execute(
                query,
                {
                    "wkt": geom.wkt,
                    "name": feature.properties.name,
                    "feature_id": feature_id
                }
            ).scalar()
            if not result:
                raise HTTPException(status_code=404, detail="Feature not found")
            return {"message": "Feature updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/features/{feature_id}")
async def delete_feature(feature_id: int):
    """Delete a feature"""
    try:
        engine = get_db_engine()
        with engine.connect() as connection:
            query = text("""
                DELETE FROM countries
                WHERE gid = :feature_id
                RETURNING gid;
            """)
            result = connection.execute(query, {"feature_id": feature_id}).scalar()
            if not result:
                raise HTTPException(status_code=404, detail="Feature not found")
            return {"message": "Feature deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
