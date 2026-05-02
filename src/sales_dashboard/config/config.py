import os
from pathlib import Path

class Config:
    """Configuration class for the Sales Dashboard application."""

    # Security settings
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-key-123")

    # Database paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    DB_PATH = BASE_DIR / "orders.db"
    USER_DB_PATH = BASE_DIR / "users.db"
    EXCEL_PATH = BASE_DIR / "wholesale_orders_final.xlsx"

    # Table name
    TABLE_NAME = "orders"

    # Admin credentials
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

    # Cache settings
    CACHE_TYPE = os.getenv("CACHE_TYPE", "SimpleCache")
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", 300))

    # Debug settings
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"