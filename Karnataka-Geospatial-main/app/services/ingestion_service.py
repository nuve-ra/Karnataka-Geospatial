import geopandas as gpd

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

from geoalchemy2.shape import from_shape

from tenacity import retry
from tenacity import stop_after_attempt

from app.database import SessionLocal
from app.models import GeoFeature
from app.utils.logger import logger


FILE_PATH = "data/karnataka.geojson"


@retry(stop=stop_after_attempt(3))
def ingest_geojson():

    logger.info(
        "Starting GeoJSON ingestion"
    )

    db: Session = SessionLocal()

    try:

        # Load GeoJSON
        gdf = gpd.read_file(FILE_PATH)

        logger.info(
            f"Loaded {len(gdf)} features"
        )

        # Ensure CRS compatibility
        gdf = gdf.to_crs(epsg=4326)

        inserted_count = 0
        updated_count = 0
        failed_count = 0

        incoming_feature_names = set()

        for idx, row in gdf.iterrows():

            try:

                feature_name = f"feature_{idx}"

                incoming_feature_names.add(
                    feature_name
                )

                geometry_wkt = row.geometry.wkt

                existing_feature = (
                    db.query(GeoFeature)
                    .filter(
                        GeoFeature.name == feature_name
                    )
                    .first()
                )

                # UPDATE existing feature
                if existing_feature:

                    update_query = text("""

                        UPDATE geo_features
                        SET geometry = ST_GeomFromText(
                            :geometry,
                            4326
                        )
                        WHERE name = :name

                    """)

                    db.execute(
                        update_query,
                        {
                            "geometry": geometry_wkt,
                            "name": feature_name
                        }
                    )

                    updated_count += 1

                    logger.info(
                        f"Updated: {feature_name}"
                    )

                # INSERT new feature
                else:

                    geometry = from_shape(
                        row.geometry,
                        srid=4326
                    )

                    new_feature = GeoFeature(
                        name=feature_name,
                        geometry=geometry
                    )

                    db.add(new_feature)

                    inserted_count += 1

                    logger.info(
                        f"Inserted: {feature_name}"
                    )

                # Batch commit
                if idx % 20 == 0:

                    db.commit()

                    logger.info(
                        f"Committed batch up to {idx}"
                    )

            except Exception as feature_error:

                failed_count += 1

                logger.error(
                    f"Failed feature {idx}: "
                    f"{str(feature_error)}"
                )

        # Remove deleted features
        existing_features = db.query(
            GeoFeature
        ).all()

        for feature in existing_features:

            if feature.name not in incoming_feature_names:

                logger.info(
                    f"Deleting removed feature "
                    f"{feature.name}"
                )

                db.delete(feature)

        db.commit()

        logger.info(
            f"""
GeoJSON ingestion completed successfully

Inserted: {inserted_count}
Updated: {updated_count}
Failed: {failed_count}
"""
        )

    except SQLAlchemyError as db_error:

        db.rollback()

        logger.error(
            f"Database error: {str(db_error)}"
        )

    except Exception as e:

        logger.error(
            f"Ingestion failed: {str(e)}"
        )

    finally:

        db.close()

        logger.info(
            "Database session closed"
        )


if __name__ == "__main__":

    ingest_geojson()