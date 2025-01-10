import sqlite3
import os
import logging

logger = logging.getLogger(__name__)

def get_database_connection():
    """Create and return a database connection to the local database."""
    try:
        # Use a simple relative path from the project root
        database_path = 'DATABASE/401kDATABASE.db'
        
        if not os.path.exists(database_path):
            raise FileNotFoundError(
                "Database file not found. Please ensure:\n"
                "1. The DATABASE folder exists in the project root\n"
                f"2. The database file exists at: {database_path}"
            )

        return sqlite3.connect(database_path)
        
    except Exception as e:
        logger.error(f"Error connecting to database: {str(e)}")
        raise