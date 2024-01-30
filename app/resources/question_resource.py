from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.models import Question


class QuestionResource(Resource):
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()

        data = request.json

        if not data:
            return {'message': 'No data provided in the request'}, 400

        if isinstance(data, list):
            # If the data is a list, add multiple questions
            questions_list = []

            for item in data:
                question_text = item.get('question')
                answer_text = item.get('answer')

                if not question_text or not answer_text:
                    return {'message': 'Question and answer cannot be empty'}, 400

                new_question = Question(user_id=current_user_id, question=question_text, answer=answer_text)
                questions_list.append(new_question)

            db.session.add_all(questions_list)
            db.session.commit()

            return {'message': 'Questions added successfully'}, 201
        elif isinstance(data, dict):
            # If the data is not a list, add a single question
            question_text = data.get('question')
            answer_text = data.get('answer')

            if not question_text or not answer_text:
                return {'message': 'Question and answer cannot be empty'}, 400

            new_question = Question(user_id=current_user_id, question=question_text, answer=answer_text)

            db.session.add(new_question)
            db.session.commit()

            return {'message': 'Question added successfully'}, 201
        else:
            return {'message': 'Invalid format for adding questions'}, 400

    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()

        try:
            # Filter questions based on the user_id
            questions = Question.query.filter_by(user_id=current_user_id).all()
            questions_list = []

            if not questions:
                return {'message': 'No questions have been created yet for the user'}, 404

            for question in questions:
                question_data = {
                    'id': question.id,
                    'question': question.question,
                    'answer': question.answer
                }
                questions_list.append(question_data)

            return {'questions': questions_list}, 200

        except Exception as e:
            return {'message': 'An error occurred while fetching questions'}, 500

    @jwt_required()
    def put(self):
        current_user_id = get_jwt_identity()

        data = request.json

        if isinstance(data, list):
            # If the data is a list, update multiple questions
            updated_count = 0
            for item in data:
                question_text = item.get('question')
                new_answer_text = item.get('new_answer')

                # Find the question by ID
                question = Question.query.filter_by(question=question_text, user_id=current_user_id).first()

                if question:
                    # Update question fields if provided
                    if new_answer_text:
                        question.answer = new_answer_text
                        updated_count += 1

            db.session.commit()

            if updated_count > 0:
                return {'message': 'Questions updated successfully'}, 200
            else:
                return {'message': 'No questions found for update'}, 404
        elif isinstance(data, dict):
            # If the data is not a list, update a single question
            question_text = data.get('question')
            new_answer_text = data.get('new_answer')

            # Find the question by ID
            question = Question.query.filter_by(question=question_text, user_id=current_user_id).first()

            if not question:
                return {'message': 'Question not found for the user'}, 404

            # Update question fields if provided
            if new_answer_text:
                question.answer = new_answer_text

            db.session.commit()

            return {'message': 'Question updated successfully'}, 200
        else:
            return {'message': 'Invalid format for updating questions'}, 400

    @jwt_required()
    def delete(self, question_id=None):
        current_user_id = get_jwt_identity()

        try:
            if question_id is None:
                # If no question_id is provided, delete all questions for the user
                deleted_count = Question.query.filter_by(user_id=current_user_id).delete()
            else:
                # Delete a single question by ID
                deleted_count = Question.query.filter_by(id=question_id, user_id=current_user_id).delete()

            db.session.commit()

            if deleted_count > 0:
                return {'message': 'Question(s) deleted successfully'}, 200
            else:
                return {'message': 'No questions found for deletion'}, 404

        except Exception as e:
            return {'message': 'An error occurred while deleting question(s)'}, 500
