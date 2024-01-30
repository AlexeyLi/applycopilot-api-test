from datetime import datetime
from flask_restful import Resource
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity)
from flask import request

from app.models.models import UserProfile
from app.extensions import db


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
                user_profile.date_of_birth = datetime.strptime(date_of_birth_str, '%m-%d-%Y').date()
            if address:
                user_profile.address = address

            db.session.commit()

            return {'message': 'User profile updated successfully'}, 200

        except ValueError:
            return {'message': 'Invalid date format. Please use "MM-DD-YYYY"'}, 400
        except Exception as e:
            return {'message': 'An error occurred while updating user profile'}, 500
