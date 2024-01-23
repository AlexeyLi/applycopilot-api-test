# resources.py
from flask_login import logout_user
from flask_restful import Resource
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask import request
from models import User, UserProfile, db, bcrypt, load_user

from datetime import datetime

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


class UserLogin(Resource):
    def post(self):
        username = request.json.get('username')
        password = request.json.get('password')

        user = User.query.filter_by(username=username).first()

        if not user:
            return {'error': 'User not found'}, 401

        if user and bcrypt.check_password_hash(user.hashed_password, password):
            access_token = create_access_token(identity=user.id)
            return {'access_token': access_token}, 200
        else:
            return {'error': 'Invalid username or password'}, 401


class UserProfileResource(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()

        try:
            user_profile = UserProfile.query.filter_by(user_id=current_user_id).first()

            if not user_profile:
                return {'message': 'User profile not found'}, 404

            profile_data = {
                'id': user_profile.id,
                'full_name': user_profile.full_name,
                'date_of_birth': user_profile.date_of_birth.isoformat() if user_profile.date_of_birth else None,
                'address': user_profile.address
            }

            return {'profile': profile_data}, 200

        except Exception as e:
            return {'message': 'An error occurred while fetching user profile'}, 500

    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()

        try:
            user_profile = UserProfile.query.filter_by(user_id=current_user_id).first()

            if user_profile:
                return {'message': 'User profile already exists. Use PUT to update.'}, 400

            full_name = request.json.get('full_name')
            date_of_birth_str = request.json.get('date_of_birth')
            address = request.json.get('address')

            # Convert the date_of_birth string to a Date object
            date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date() if date_of_birth_str else None

            new_user_profile = UserProfile(
                user_id=current_user_id,
                full_name=full_name,
                date_of_birth=date_of_birth,
                address=address
            )

            db.session.add(new_user_profile)
            db.session.commit()

            return {'message': 'User profile created successfully'}, 201

        except ValueError:
            return {'message': 'Invalid date format. Please use "YYYY-MM-DD"'}, 400
        except Exception as e:
            return {'message': 'An error occurred while creating user profile'}, 500

    @jwt_required()
    def put(self):
        current_user_id = get_jwt_identity()

        try:
            user_profile = UserProfile.query.filter_by(user_id=current_user_id).first()

            if not user_profile:
                return {'message': 'User profile not found. Use POST to create.'}, 404

            full_name = request.json.get('full_name')
            date_of_birth_str = request.json.get('date_of_birth')
            address = request.json.get('address')

            # Update user profile fields if provided
            if full_name:
                user_profile.full_name = full_name
            if date_of_birth_str:
                user_profile.date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
            if address:
                user_profile.address = address

            db.session.commit()

            return {'message': 'User profile updated successfully'}, 200

        except ValueError:
            return {'message': 'Invalid date format. Please use "YYYY-MM-DD"'}, 400
        except Exception as e:
            return {'message': 'An error occurred while updating user profile'}, 500
