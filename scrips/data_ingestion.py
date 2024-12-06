import os
import requests
import geopandas as gpd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import traceback

# Load environment variables
load_dotenv()

def create_db_engine():
    """Create database connection engine using environment variables."""
    try:
        db_params = {
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD')
        }
        
        # Print connection details (except password)
        print(f"Connecting to database: {db_params['database']}")
        print(f"Host: {db_params['host']}")
        print(f"Port: {db_params['port']}")
        print(f"User: {db_params['user']}")
        
        connection_string = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
        return create_engine(connection_string)
    except Exception as e:
        print(f"Error creating database engine: {str(e)}")
        print(traceback.format_exc())
        raise

def fetch_geojson(url):
    """Fetch GeoJSON data from the specified URL."""
    try:
        print(f"Fetching data from URL: {url}")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(f"Successfully fetched data with {len(data['features'])} features")
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching GeoJSON data: {str(e)}")
        print(traceback.format_exc())
        return None

def process_and_store_data(url, table_name):
    """Main function to process and store GeoJSON data."""
    try:
        # Fetch GeoJSON data
        geojson_data = fetch_geojson(url)
        
        if not geojson_data:
            return False
        
        # Convert to GeoDataFrame
        print("Converting to GeoDataFrame...")
        gdf = gpd.GeoDataFrame.from_features(geojson_data['features'])
        print(f"Created GeoDataFrame with {len(gdf)} rows")
        
        # Ensure CRS is set to EPSG:4326 (WGS 84)
        if gdf.crs is None:
            print("Setting CRS to EPSG:4326...")
            gdf.set_crs(epsg=4326, inplace=True)
        else:
            print(f"Converting from {gdf.crs} to EPSG:4326...")
            gdf = gdf.to_crs(epsg=4326)
        
        # Create database connection
        print("Creating database connection...")
        engine = create_db_engine()
        
        # Store in PostgreSQL with PostGIS
        print(f"Storing data in table '{table_name}'...")
        gdf.to_postgis(
            name=table_name,
            con=engine,
            if_exists='replace',
            index=False
        )
        
        print(f"Successfully stored {len(gdf)} records in table '{table_name}'")
        return True
        
    except Exception as e:
        print(f"Error processing or storing data: {str(e)}")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    # Example using a public GeoJSON API (Natural Earth Data - Countries)
    geojson_url = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
    table_name = "countries"
    
    success = process_and_store_data(geojson_url, table_name)
    if success:
        print("Data ingestion completed successfully")
        
        # Verify the data
        try:
            engine = create_db_engine()
            with engine.connect() as connection:
                result = connection.execute("SELECT COUNT(*) FROM countries").fetchone()
                print(f"Verified {result[0]} records in the countries table")
        except Exception as e:
            print(f"Error verifying data: {str(e)}")
    else:
        print("Data ingestion failed")
