from sqlalchemy import Column, Integer, String
from geoalchemy2 import Geometry

from app.database import Base


class GeoFeature(Base):

    __tablename__ = "geo_features"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        unique=True
    )

    geometry = Column(
        Geometry(
            geometry_type="GEOMETRY",
            srid=4326
        )
    )