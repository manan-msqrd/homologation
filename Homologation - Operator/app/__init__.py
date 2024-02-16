from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
import logging
from logging.handlers import RotatingFileHandler
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import timedelta


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Deevia@123_homologation'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Deevia%40123@localhost/homologation'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_EXPIRATION_DELTA'] = timedelta(days=1)

CORS(app, supports_credentials=True)
socketio = SocketIO(app)
jwt = JWTManager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

logger = logging.getLogger('my_logger')
logger.setLevel(logging.INFO)

# Configure the logger with FileHandler
handler = RotatingFileHandler('app.log', maxBytes=1e6, backupCount=0)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] - %(message)s'))
logger.addHandler(handler)


from app import routes, models