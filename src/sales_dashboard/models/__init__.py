import sqlite3
from pathlib import Path
import os

# Database paths
DB_PATH = Path(__file__).resolve().parent.parent / "orders.db"
USER_DB_PATH = Path(__file__).resolve().parent.parent / "users.db"
TABLE_NAME = "orders"

def get_connection():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    """Initialize the main database connection."""
    pass

def initialize_user_database():
    """Initialize the user database."""
    pass