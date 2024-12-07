import geopandas as gpd
from sqlalchemy import create_engine
from geoalchemy2 import Geometry
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

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

def load_karnataka_data():
    try:
        # Read the GeoJSON file
        print("Reading Karnataka GeoJSON file...")
        gdf = gpd.read_file("karnataka.geojson")
        
        # Ensure the CRS is set to EPSG:4326 (WGS 84)
        if gdf.crs is None:
            gdf.set_crs(epsg=4326, inplace=True)
        else:
            gdf = gdf.to_crs(epsg=4326)
        
        # Add a name column if it doesn't exist
        if 'name' not in gdf.columns:
            gdf['name'] = 'Karnataka Region'
        
        # Create database connection
        print("Connecting to database...")
        engine = get_db_engine()
        
        # Write to PostGIS
        print("Writing to database...")
        gdf.to_postgis(
            name='countries',
            con=engine,
            if_exists='append',
            index=False,
            dtype={'geometry': Geometry('GEOMETRY', srid=4326)}
        )
        
        print("Data loaded successfully!")
        return True
        
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    load_karnataka_data()
