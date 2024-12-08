import os
from dotenv import load_dotenv
import pg8000

# Load environment variables
load_dotenv()

def check_samples():
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
        
        # Get 5 sample features with their full data
        cur.execute("""
            SELECT id, name, 
                   geometry->>'type' as geom_type,
                   geometry->'coordinates'->0->0->0 as first_lon,
                   geometry->'coordinates'->0->0->1 as first_lat
            FROM features 
            LIMIT 5
        """)
        samples = cur.fetchall()
        
        print("\nSample features:")
        for id, name, geom_type, first_lon, first_lat in samples:
            print(f"\nID: {id}")
            print(f"Name: {name}")
            print(f"Geometry Type: {geom_type}")
            print(f"First Coordinate: [{first_lon}, {first_lat}]")
            
    except Exception as e:
        print(f"Error checking samples: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_samples()
