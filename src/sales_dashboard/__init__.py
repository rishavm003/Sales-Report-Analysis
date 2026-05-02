from flask import Flask
from flask_caching import Cache
from sales_dashboard.config.config import Config

app = Flask(__name__)

# Load configuration
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['CACHE_TYPE'] = Config.CACHE_TYPE
app.config['CACHE_DEFAULT_TIMEOUT'] = Config.CACHE_DEFAULT_TIMEOUT

cache = Cache(app)

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=5000)