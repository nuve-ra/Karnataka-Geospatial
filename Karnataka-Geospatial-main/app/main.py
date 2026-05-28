from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.geo_routes import router
from app.tasks.scheduler import start_scheduler


app = FastAPI(
    title="Karnataka Geospatial API",
    version="1.0.0",
    description="""
    Automated Geospatial Data Ingestion
    and Spatial Query API for Karnataka
    using FastAPI + PostGIS
    """
)

# -----------------------------------
# CORS
# -----------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------
# ROUTES
# -----------------------------------

app.include_router(router)

# -----------------------------------
# STARTUP EVENT
# -----------------------------------

@app.on_event("startup")
def startup_event():

    start_scheduler()

# -----------------------------------
# ROOT ENDPOINT
# -----------------------------------

@app.get("/")
def root():

    return {
        "message": (
            "Karnataka Geospatial API running"
        ),
        "docs": "/docs",
        "health": "/health"
    }

# -----------------------------------
# HEALTH CHECK
# -----------------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }