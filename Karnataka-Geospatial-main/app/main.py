from fastapi import FastAPI

from app.routes.geo_routes import router
from app.tasks.scheduler import start_scheduler

app = FastAPI(
    title="Karnataka Geospatial API",
    version="1.0.0"
)

app.include_router(router)


@app.on_event("startup")
def startup_event():

    start_scheduler()


@app.get("/")
def root():

    return {
        "message": "Karnataka Geospatial API running"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }