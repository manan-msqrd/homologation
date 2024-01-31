import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_login import LoginManager
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

app.config['SECRET_KEY'] = 'Deevia@123_homologation'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Deevia%40123@localhost/homologation'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_NAME'] = 'session'


CORS(app, supports_credentials=True)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

logger = logging.getLogger('my_logger')
logger.setLevel(logging.INFO)

# Configure the logger with FileHandler
handler = RotatingFileHandler('app.log', maxBytes=1e6, backupCount=0)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] - %(message)s'))
logger.addHandler(handler)

from app import routes, models

















# from flask import Flask, json
# from flask_sockets import Sockets
# from gevent import pywsgi
# from geventwebsocket.handler import WebSocketHandler
# import cv2
# import base64
# from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = ''
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)
# bcrypt = Bcrypt(app)
# sockets = Sockets(app)

# from app import routes











# def write_data_to_file(data, filename):
#     with open(filename, 'w') as json_file:
#         json.dump(data, json_file, indent=4)

# def read_data_from_file(filename):
#     try:
#         with open(filename, 'r') as json_file:
#             data = json.load(json_file)
#             return data
#     except FileNotFoundError:
#         return None


# class VideoCapture:
#     def __init__(self):
#         self.video_capture = None
#         self.video_filename = None
#         self.video_frame = None

#     def init_video_capture(self, rtsp_url):
#         try:
#             cap = cv2.VideoCapture(rtsp_url)
#             if not cap.isOpened():
#                 raise Exception("Error opening RTSP stream")
#             return cap
#         except Exception as e:
#             print(f"Error initializing video capture: {e}")
#             return None
