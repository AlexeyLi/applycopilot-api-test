from flask_restful import Resource
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token,
    create_refresh_token)
from flask import request, jsonify

from app.models.models import User
from app.extensions import bcrypt


class UserLogin(Resource):
    def post(self):
        username = request.json.get('username')
        password = request.json.get('password')

        user = User.query.filter_by(username=username).first()

        if not user:
            return {'error': 'User not found'}, 401

        if user and bcrypt.check_password_hash(user.hashed_password, password):
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)

            return {'access_token': access_token, 'refresh_token': refresh_token}, 200
        else:
            return {'error': 'Invalid username or password'}, 401

    # Refresh access token
    @jwt_required(refresh=True)
    def refresh_access_token(self):
        current_user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user_id)
        return jsonify(access_token=new_access_token), 200
