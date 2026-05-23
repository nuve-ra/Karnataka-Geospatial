import json
import os
import pg8000
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def load_karnataka_data():
    try:
        # Read the GeoJSON file
        print("Reading Karnataka GeoJSON file...")
        with open("karnataka.geojson", "r") as f:
            geojson_data = json.loads(f.read())
        
        # Connect to PostgreSQL
        conn = pg8000.connect(
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT"))
        )
        cur = conn.cursor()
        
        # First, clear existing data
        cur.execute("DELETE FROM features")
        
        # Insert features into database
        for idx, feature in enumerate(geojson_data['features'], 1):
            # Extract properties and geometry
            properties = feature.get('properties', {})
            geometry = feature['geometry']
            
            # Create a meaningful name
            name = f"Karnataka Region {idx}"
            description = f"Region {idx} in Karnataka with geometry type {geometry['type']}"
            
            # Print what we're inserting
            print(f"\nInserting feature {idx}:")
            print(f"Name: {name}")
            print(f"Geometry Type: {geometry['type']}")
            print(f"First coordinate: {geometry['coordinates'][0][0] if geometry['coordinates'] else 'No coordinates'}")
            
            # Insert into database
            cur.execute("""
                INSERT INTO features (name, description, geometry)
                VALUES (%s, %s, %s)
            """, (name, description, json.dumps(geometry)))
        
        # Commit the transaction
        conn.commit()
        print("\nSuccessfully loaded Karnataka data!")
        
        # Verify the data
        cur.execute("SELECT COUNT(*) FROM features")
        count = cur.fetchone()[0]
        print(f"Total features loaded: {count}")
        
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    load_karnataka_data()
