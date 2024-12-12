import sqlite3

def get_database_connection():
    """Create and return a database connection"""
    return sqlite3.connect('DATABASE/401kDATABASE.db') 