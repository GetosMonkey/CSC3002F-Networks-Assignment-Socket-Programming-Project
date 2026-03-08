import sqlite3
import os

DB_PATH = "database/chat_app.db"

def get_db_connection():
    """
    Creates a connection to the SQLite database with WAL mode enabled 
    to handle multiple readers and writers efficiently.
    """
    # Ensure the directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    
    # Enable Write-Ahead Logging (WAL) as per project requirements
    conn.execute("PRAGMA journal_mode=WAL;")
    
    # Enable foreign key constraints (crucial for 3-level architecture integrity)
    conn.execute("PRAGMA foreign_keys = ON;")
    
    # Allows fetching rows as dictionaries: row['username'] instead of row[0]
    conn.row_factory = sqlite3.Row
    
    return conn