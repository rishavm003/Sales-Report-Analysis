import os
import sqlite3
from pathlib import Path
import pandas as pd

# Database and file paths
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "orders.db"
USER_DB_PATH = BASE_DIR / "users.db"
TABLE_NAME = "orders"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    """Initialize the main database connection."""
    pass

def initialize_user_database():
    """Initialize the user database."""
    pass

def get_connection():
    """Get database connection."""
    pass