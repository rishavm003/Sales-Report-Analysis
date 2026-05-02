"""
Main entry point for the Sales Dashboard application.
"""

from src.sales_dashboard import app
from src.sales_dashboard.config.config import Config

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=5000)