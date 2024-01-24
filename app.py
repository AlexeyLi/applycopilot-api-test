# Import modules that need to be patched before ssl
from gevent import monkey
monkey.patch_all()

# Rest of the imports
from dotenv import load_dotenv
import logging
import json
import os

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from resources import UserResource, UserLogin, UserProfileResource
from models import db, bcrypt, login_manager


app = Flask(__name__)

load_dotenv()
logging.basicConfig(level=logging.INFO)
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)
app.config['SESSION_TYPE'] = 'filesystem'

db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)


# Function to create the database tables
def create_tables():
    db.create_all()


# Execute create_tables() before the first request is handled
@app.before_request
def before_first_request():
    create_tables()


# Clear the database when the app stops
# This is for testing purposes only, should be deleted in production
# def cleanup_database(exception=None):
#     db.session.remove()
#     db.drop_all()


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return super().default(obj)


app.json_encoder = CustomJSONEncoder

login_manager.init_app(app)
jwt = JWTManager(app)
api = Api(app)

api.add_resource(UserResource, '/register', '/user')
api.add_resource(UserLogin, '/login')
api.add_resource(UserProfileResource, '/user/profile')

app.debug = True

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

# Attach the cleanup_database function to the app's teardown_appcontext
# app.teardown_appcontext(cleanup_database)
