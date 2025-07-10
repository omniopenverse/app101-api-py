from flask import Flask
from flasgger import Swagger
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics
import logging
import os

from config import config_by_env
from extensions import db, migrate

# Ensure log dir exists
LOG_FILE = os.getenv("APP101_LOG_FILE", "/var/log/app101/app.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Configure logging to file
logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(LOG_FILE)
formatter = logging.Formatter('%(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

env = os.getenv("APP_ENV", "local")
app = Flask(__name__)
app.config.from_object(config_by_env[env])
print(f"SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

CORS(app)
db.init_app(app)
migrate.init_app(app, db)
swagger = Swagger(app)
metrics = PrometheusMetrics(app)
logging.basicConfig(level=logging.INFO)

# Import routes and models
from models import Users
from routes import *

# Initialize SQLite DB schema if needed
if app.config['SQLALCHEMY_DATABASE_URI'].startswith("sqlite:///"):
    with app.app_context():
        db.create_all()
        print("✅ SQLite DB schema ensured.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=app.config.get("DEBUG", False))