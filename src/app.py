from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flasgger import Swagger
from prometheus_flask_exporter import PrometheusMetrics
from flask_cors import CORS
import logging
import os

app = Flask(__name__)

CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SWAGGER'] = {'title': 'User API', 'uiversion': 3}

db = SQLAlchemy(app)
migrate = Migrate(app, db)

swagger = Swagger(app)
metrics = PrometheusMetrics(app)
logging.basicConfig(level=logging.INFO)

from routes import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
