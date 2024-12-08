import pg8000
import os
from dotenv import load_dotenv

def check_database():
    # Database connection parameters
    db_params = {
        'database': 'postgis_35',
        'user': 'postgres',
        'password': 'Mymobile11',
        'host': 'localhost',
        'port': 5432
    }
    
    try:
        print("\n=== Database Connection Check ===")
        conn = pg8000.connect(**db_params)
        cursor = conn.cursor()
        print("✓ Successfully connected to PostgreSQL database!")
        
        # Check PostGIS extension
        print("\n=== PostGIS Extension Check ===")
        cursor.execute("SELECT PostGIS_version();")
        postgis_version = cursor.fetchone()[0]
        print(f"✓ PostGIS version: {postgis_version}")
        
        # List all tables
        print("\n=== Tables in Database ===")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        if tables:
            for table in tables:
                print(f"- {table[0]}")
                
                # If it's the features table, show count and sample
                if table[0] == 'features':
                    cursor.execute("SELECT COUNT(*) FROM features")
                    count = cursor.fetchone()[0]
                    print(f"  → Total features: {count}")
                    
                    if count > 0:
                        print("\n=== Sample Feature ===")
                        cursor.execute("""
                            SELECT name, ST_AsGeoJSON(geometry) as geom
                            FROM features 
                            LIMIT 1
                        """)
                        sample = cursor.fetchone()
                        if sample:
                            print(f"Name: {sample[0]}")
                            print(f"Geometry: {sample[1][:100]}...")
        else:
            print("No tables found in the database.")
        
        cursor.close()
        conn.close()
        print("\n✓ Database check completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check if database 'postgis_35' exists")
        print("3. Verify PostGIS extension is installed")
        print("4. Check if the database user has proper permissions")

if __name__ == "__main__":
    check_database()
