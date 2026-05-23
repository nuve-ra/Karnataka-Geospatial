import os
from dotenv import load_dotenv
import pg8000
import json

# Load environment variables
load_dotenv()

def verify_data():
    try:
        # Connect to PostgreSQL
        conn = pg8000.connect(
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT"))
        )
        cur = conn.cursor()
        
        # Get total count
        cur.execute("SELECT COUNT(*) FROM features")
        total_count = cur.fetchone()[0]
        print(f"\nTotal features in database: {total_count}")
        
        # Check for NULL values
        cur.execute("SELECT COUNT(*) FROM features WHERE name IS NULL OR geometry IS NULL")
        null_count = cur.fetchone()[0]
        print(f"Features with NULL values: {null_count}")
        
        # Get geometry types
        cur.execute("SELECT geometry->>'type' as geometry_type, COUNT(*) FROM features GROUP BY geometry->>'type'")
        geometry_types = cur.fetchall()
        print("\nGeometry types:")
        for gtype, count in geometry_types:
            print(f"- {gtype}: {count}")
        
        # Get coordinate ranges
        cur.execute("""
            SELECT 
                MIN(CAST(geometry->'coordinates'->0->0->0 AS FLOAT)) as min_longitude,
                MAX(CAST(geometry->'coordinates'->0->0->0 AS FLOAT)) as max_longitude,
                MIN(CAST(geometry->'coordinates'->0->0->1 AS FLOAT)) as min_latitude,
                MAX(CAST(geometry->'coordinates'->0->0->1 AS FLOAT)) as max_latitude
            FROM features
        """)
        bounds = cur.fetchone()
        print(f"\nCoordinate ranges:")
        print(f"Longitude: {bounds[0]:.6f}°E to {bounds[1]:.6f}°E")
        print(f"Latitude: {bounds[2]:.6f}°N to {bounds[3]:.6f}°N")
        
        # Sample some features
        cur.execute("SELECT id, name, geometry->>'type' FROM features LIMIT 5")
        print("\nSample features:")
        for id, name, gtype in cur.fetchall():
            print(f"- ID {id}: {name} ({gtype})")
            
    except Exception as e:
        print(f"Error verifying data: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    verify_data()
