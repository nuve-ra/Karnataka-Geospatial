import os
import sys
import logging
from datetime import datetime
from data_ingestion import process_and_store_data
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('geojson_update.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def check_for_updates(engine, table_name, new_data_count):
    """Compare the current data count with new data count"""
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text(f"SELECT COUNT(*) FROM {table_name}")
            ).scalar()
            return result != new_data_count
    except Exception as e:
        logging.error(f"Error checking for updates: {e}")
        return True

def backup_table(engine, table_name):
    """Create a backup of the current table"""
    backup_name = f"{table_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        with engine.connect() as connection:
            connection.execute(
                text(f"CREATE TABLE {backup_name} AS SELECT * FROM {table_name}")
            )
        logging.info(f"Created backup table: {backup_name}")
        return True
    except Exception as e:
        logging.error(f"Error creating backup: {e}")
        return False

def main():
    """Main function to run the automated update"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Configuration
        geojson_url = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
        table_name = "countries"
        
        logging.info("Starting automated update process")
        
        # Create database engine
        db_params = {
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD')
        }
        engine = create_engine(
            f"postgresql://{db_params['user']}:{db_params['password']}@"
            f"{db_params['host']}:{db_params['port']}/{db_params['database']}"
        )
        
        # Process the new data
        success = process_and_store_data(geojson_url, f"{table_name}_temp")
        
        if success:
            # Check if there are any changes
            with engine.connect() as connection:
                new_count = connection.execute(
                    text(f"SELECT COUNT(*) FROM {table_name}_temp")
                ).scalar()
            
            if check_for_updates(engine, table_name, new_count):
                logging.info("Changes detected in the data")
                
                # Create backup
                if backup_table(engine, table_name):
                    # Replace the old table with the new one
                    with engine.connect() as connection:
                        connection.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
                        connection.execute(
                            text(f"ALTER TABLE {table_name}_temp RENAME TO {table_name}")
                        )
                    logging.info("Successfully updated the data")
                else:
                    logging.error("Failed to create backup, update aborted")
            else:
                logging.info("No changes detected in the data")
                # Clean up temporary table
                with engine.connect() as connection:
                    connection.execute(text(f"DROP TABLE IF EXISTS {table_name}_temp"))
        else:
            logging.error("Failed to process and store new data")
            
    except Exception as e:
        logging.error(f"Error in automated update: {e}")
        raise

if __name__ == "__main__":
    main()