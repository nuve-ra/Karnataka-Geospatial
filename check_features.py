import os
from dotenv import load_dotenv
import pg8000

# Load environment variables
load_dotenv()

def check_features():
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
        
        # Get count of features
        cur.execute("SELECT COUNT(*) FROM features")
        count = cur.fetchone()[0]
        print(f"\nTotal features in table: {count}")
        
        # Get table structure
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'features'
        """)
        columns = cur.fetchall()
        print("\nTable structure:")
        for column, dtype in columns:
            print(f"- {column}: {dtype}")
            
    except Exception as e:
        print("Error checking features table:")
        print(str(e))
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_features()
