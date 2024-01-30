from flask import Flask, jsonify
from flask_restful import Api
from jwt.exceptions import ExpiredSignatureError

from .models.models import User, UserProfile, Question
from .resources.user_resource import UserResource
from .resources.user_login_resource import UserLogin
from .resources.user_profile_resource import UserProfileResource
from .resources.question_resource import QuestionResource

import json
from dotenv import load_dotenv

from .config import Config
from .extensions import db, bcrypt, jwt, login_manager

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)


bcrypt.init_app(app)
db.init_app(app)
jwt.init_app(app)
login_manager.init_app(app)


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return super().default(obj)


app.json_encoder = CustomJSONEncoder


# Create database tables before the first request is handled
@app.before_request
def before_first_request():
    db.create_all()


api = Api(app)

api.add_resource(UserResource, '/register', '/user')
api.add_resource(UserLogin, '/login', '/refresh')
api.add_resource(UserProfileResource, '/user/profile')
api.add_resource(QuestionResource, '/questions')


# Catch ExpiredSignatureError and return a message for expired token
@app.errorhandler(ExpiredSignatureError)
def handle_expired_token_error(error):
    app.logger.debug(error)
    return jsonify({"message": "Token has expired"}), 401


app.debug = False

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
