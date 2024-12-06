import geopandas as gpd
from sqlalchemy import create_engine, URL
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Load environment variables
load_dotenv()

def get_db_connection():
    try:
        # Get database parameters from environment variables
        db_params = {
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD')
        }
        
        # Create the connection URL
        url_object = URL.create(
            "postgresql+psycopg2",
            username=db_params['user'],
            password=db_params['password'],
            host=db_params['host'],
            port=db_params['port'],
            database=db_params['database']
        )
        
        return create_engine(url_object)
    except Exception as e:
        print(f"Error creating database connection: {str(e)}")
        return None

def load_karnataka_data():
    try:
        # Read the GeoJSON file
        print("Reading Karnataka GeoJSON file...")
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'karnataka.geojson')
        gdf = gpd.read_file(file_path)
        
        print(f"Loaded {len(gdf)} features from GeoJSON")
        
        # Ensure the CRS is set to EPSG:4326 (WGS 84)
        if gdf.crs is None:
            print("Setting CRS to EPSG:4326...")
            gdf.set_crs(epsg=4326, inplace=True)
        else:
            print(f"Converting from {gdf.crs} to EPSG:4326...")
            gdf = gdf.to_crs(epsg=4326)
        
        # Add a name column if it doesn't exist
        if 'name' not in gdf.columns:
            print("Adding name column...")
            gdf['name'] = 'Karnataka Region'
        
        # Create database connection
        print("Connecting to database...")
        engine = get_db_connection()
        
        if engine is None:
            print("Failed to create database connection")
            return False
        
        # Write to PostGIS
        print("Writing to database...")
        gdf.to_postgis(
            name='countries',
            con=engine,
            if_exists='append',
            index=False
        )
        
        print("Data loaded successfully!")
        return True
        
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        print("Error details:", e.__class__.__name__)
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    load_karnataka_data()
