from fastapi import APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi.responses import JSONResponse
from ..schema.feature_schema import FeatureResponse

import json

from app.database import SessionLocal
from app.models import GeoFeature
from app.utils.logger import logger

router = APIRouter(
    prefix="/features",
    tags=["Features"]
)


# -----------------------------------
# GET ALL FEATURES
# -----------------------------------

@router.get(
    "/",
    response_model=list[FeatureResponse]
)
def get_features(
    skip: int = 0,
    limit: int = 10
):

    logger.info(
        f"Fetching features skip={skip}, limit={limit}"
    )

    db: Session = SessionLocal()
    try:

        features = db.query(
            GeoFeature
        ).offset(skip).limit(limit).all()

        result = []

        for feature in features:

            result.append({
                "id": feature.id,
                "name": feature.name
            })

        return result

    except Exception as e:

        logger.error(
            f"Error fetching features: {str(e)}"
        )

        return {
            "error": "Failed to fetch features"
        }

    finally:

        db.close()

# -----------------------------------
# NEARBY SEARCH
# -----------------------------------

@router.get("/nearby/")
def nearby_features(
    lon: float,
    lat: float,
    radius: float = 1000
):

    logger.info(
        f"Nearby search lon={lon}, lat={lat}, radius={radius}"
    )

    db: Session = SessionLocal()

    try:

        query = text("""

            SELECT
                id,
                name
            FROM geo_features
            WHERE ST_DWithin(
                geometry::geography,
                ST_SetSRID(
                    ST_MakePoint(:lon, :lat),
                    4326
                )::geography,
                :radius
            )

        """)

        results = db.execute(
            query,
            {
                "lon": lon,
                "lat": lat,
                "radius": radius
            }
        )

        data = []

        for row in results:

            data.append({
                "id": row.id,
                "name": row.name
            })

        return data

    except Exception as e:

        logger.error(
            f"Error in nearby search: {str(e)}"
        )

        return {
            "error": "Nearby search failed"
        }

    finally:

        db.close()


# -----------------------------------
# BOUNDING BOX SEARCH
# -----------------------------------

@router.get("/bbox/")
def bbox_search(
    minx: float,
    miny: float,
    maxx: float,
    maxy: float
):

    logger.info(
        f"BBOX search: {minx}, {miny}, {maxx}, {maxy}"
    )

    db: Session = SessionLocal()

    try:

        query = text("""

            SELECT
                id,
                name
            FROM geo_features
            WHERE ST_Intersects(
                geometry,
                ST_MakeEnvelope(
                    :minx,
                    :miny,
                    :maxx,
                    :maxy,
                    4326
                )
            )

        """)

        results = db.execute(
            query,
            {
                "minx": minx,
                "miny": miny,
                "maxx": maxx,
                "maxy": maxy
            }
        )

        data = []

        for row in results:

            data.append({
                "id": row.id,
                "name": row.name
            })

        return data

    except Exception as e:

        logger.error(
            f"Error in bbox search: {str(e)}"
        )

        return {
            "error": "BBOX search failed"
        }

    finally:

        db.close()


# -----------------------------------
# GEOJSON RESPONSE
# -----------------------------------

@router.get("/geojson/{feature_id}")
def get_feature_geojson(feature_id: int):

    logger.info(
        f"Fetching GeoJSON feature id={feature_id}"
    )

    db: Session = SessionLocal()

    try:

        query = text("""

            SELECT
                id,
                name,
                ST_AsGeoJSON(geometry) AS geometry
            FROM geo_features
            WHERE id = :feature_id

        """)

        result = db.execute(
            query,
            {
                "feature_id": feature_id
            }
        ).fetchone()

        if not result:

            return {
                "error": "Feature not found"
            }

        geojson_feature = {
            "type": "Feature",
            "geometry": json.loads(result.geometry),
            "properties": {
                "id": result.id,
                "name": result.name
            }
        }

        return JSONResponse(
            content=geojson_feature
        )

    except Exception as e:

        logger.error(
            f"Error fetching GeoJSON: {str(e)}"
        )

        return {
            "error": "Failed to fetch GeoJSON"
        }

    finally:

        db.close()


# -----------------------------------
# GET FEATURE BY ID
# -----------------------------------

@router.get("/{feature_id}")
def get_feature(feature_id: int):

    logger.info(
        f"Fetching feature id={feature_id}"
    )

    db: Session = SessionLocal()

    try:

        feature = db.query(
            GeoFeature
        ).filter(
            GeoFeature.id == feature_id
        ).first()

        if not feature:

            return {
                "error": "Feature not found"
            }

        return {
            "id": feature.id,
            "name": feature.name
        }

    except Exception as e:

        logger.error(
            f"Error fetching feature: {str(e)}"
        )

        return {
            "error": "Failed to fetch feature"
        }

    finally:

        db.close()