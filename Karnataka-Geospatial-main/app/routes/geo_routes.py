from fastapi import APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi.responses import JSONResponse
from app.schema.feature_schema import FeatureResponse
from shapely.geometry import shape
from geoalchemy2.shape import from_shape

import json

from app.database import SessionLocal
from app.models import GeoFeature
from app.utils.logger  import logger

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
# CREATE NEW FEATURE
# -----------------------------------

@router.post("/")
def create_feature(
    feature: dict
):

    db: Session = SessionLocal()

    try:

        geometry_data = feature.get(
            "geometry"
        )

        geometry_shape = shape(
            geometry_data
        )

        geometry = from_shape(
            geometry_shape,
            srid=4326
        )

        new_feature = GeoFeature(
            name=feature.get("name"),
            geometry=geometry
        )

        db.add(new_feature)

        db.commit()

        db.refresh(new_feature)

        return {
            "message": "Feature created",
            "id": new_feature.id
        }

    except Exception as e:

        logger.error(
            f"Error creating feature: {str(e)}"
        )

        return {
            "error": "Failed to create feature"
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



# -------------------------
# GET ALL GEOJSON FEATURES
# -------------------------

@router.get("/geojson/all")
def get_all_geojson():

    db: Session = SessionLocal()

    query = text("""

        SELECT
            id,
            name,
            ST_AsGeoJSON(geometry) AS geometry
        FROM geo_features

    """)

    results = db.execute(query)

    features = []

    for row in results:

        features.append({
            "type": "Feature",
            "geometry": json.loads(
                row.geometry
            ),
            "properties": {
                "id": row.id,
                "name": row.name
            }
        })

    db.close()

    return {
        "type": "FeatureCollection",
        "features": features
    }

# -----------------------------------
# GET SINGLE GEOJSON FEATURE
# -----------------------------------

@router.get("/geojson/{feature_id}")
def get_feature_geojson(
    feature_id: int
):

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
            "geometry": json.loads(
                result.geometry
            ),
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
       
# ---------------------------------
# DELETE FEATURE
# ---------------------------------

@router.delete("/{feature_id}")
def delete_feature(
    feature_id: int
):

    logger.info(
        f"Deleting feature id={feature_id}"
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

        db.delete(feature)

        db.commit()

        return {
            "message": "Feature deleted successfully"
        }

    except Exception as e:

        logger.error(
            f"Delete failed: {str(e)}"
        )

        return {
            "error": "Failed to delete feature"
        }

    finally:

        db.close()

# --------------------------------- # UPDATE FEATURE # ---------------------------------
@router.put("/{feature_id}")
def update_feature(
    feature_id: int,
    feature_data: dict
):
        logger.info(
            f"Updating feature id={feature_id}"
        )

        db: Session =SessionLocal()
        try:

            #Finding existing features
            feature = db.query(
                GeoFeature
            ).filter(
                GeoFeature.id == feature_id
            ).first()

            if not feature:

                return{
                    "error":"Feature not found"
                }
            #Updating Name
            feature.name = feature_data.get(
                "name",
                feature.name
            )

            #Updating Geometry
            geometry_data=feature_data.get(
                "geometry"
            )

            if geometry_data:
                geometry_shape=shape(
                    geometry_data
                )

                geometry=from_shape(
                    geometry_shape,
                    srid=4326
                )

                feature.geometry=geometry
            db.commit()

            return{
                "message":"Feature updated successully"
            }
        except Exception as e:

            logger.error(
                f"Update failed: {str(e)}"
            )

            db.rollback()

            return{
                "error":"Failed to update feature"
            }
        finally:
            db.close()
        