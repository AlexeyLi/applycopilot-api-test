from flask_login import logout_user
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from app.models.models import User, load_user
from app.extensions import db, bcrypt


class UserResource(Resource):
    def post(self):
        username = request.json.get('username')
        password = request.json.get('password')
        confirm_password = request.json.get('confirm_password')

        if not username or not password or not confirm_password:
            return {'message': 'Username, password, and confirm password are required'}, 400

        if password != confirm_password:
            return {'message': 'Passwords do not match'}, 400

        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            return {'message': 'Username already exists'}, 409

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create a new user
        new_user = User(username=username, hashed_password=hashed_password)

        # Save the new user to the database
        db.session.add(new_user)
        db.session.commit()
        return {'message': 'User registered successfully'}, 201

    @jwt_required()
    def delete(self):
        current_user_id = get_jwt_identity()

        # Query the User model to get the user instance
        current_user = load_user(current_user_id)

        if current_user:
            db.session.delete(current_user)
            db.session.commit()
            logout_user()
            return {'message': 'User deleted successfully'}, 200
        else:
            return {'message': 'User not found'}, 404
