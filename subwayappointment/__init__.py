from flask import Flask
from flask_redis import FlaskRedis
from flask_cors import *

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config.from_pyfile("config.py")
redis_client = FlaskRedis(app, decode_responses=True)

from subwayappointment import routeRegister
