from flask import request, jsonify
from app import app, db
from models import Users
from flasgger.utils import swag_from
import logging
import json

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'time': self.formatTime(record, self.datefmt),
        }
        return json.dumps(log_record)

# Set JSON formatter for this module's logger
logger = logging.getLogger(__name__)
for handler in logger.handlers:
    handler.setFormatter(JsonFormatter())
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)

@app.route('/health', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'Health check',
            'examples': {'status': 'ok'}
        }
    }
})
def health_check():
    """
    Health check endpoint.
    Returns a simple JSON response to indicate the service is running.
    """
    logger.info(json.dumps({'event': 'health_check', 'endpoint': '/health'}))
    return jsonify({'status': 'ok'}), 200

@app.route('/users', methods=['GET'])
@swag_from({
    'responses': {
        200: {'description': 'List of users', 'schema': {'type': 'array', 'items': {'type': 'object'}}},
        201: {'description': 'No users found'}
    }
})
def get_all_users():
    logger.info(json.dumps({'event': 'get_all_users', 'endpoint': '/users'}))
    users = Users.query.all()  # Query all users
    if users:
        logger.info(json.dumps({'event': 'users_found', 'count': len(users)}))
        return jsonify([{
                         'name': user.name,
                         'age': user.age,
                         'email': user.email
                        } for user in users
                    ]), 200
    logger.info(json.dumps({'event': 'no_users_found'}))
    return jsonify({'info': 'No users found'}), 201

@app.route('/user/<name>', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'User age',
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'age': {'type': 'integer'},
                    'email': {'type': 'string'}
                }
            }
        },
        404: {
            'description': 'User not found'
        }
    },
    'parameters': [
        {
            'name': 'name',  # The parameter name in the URL
            'in': 'path',    # The location of the parameter (in the URL path)
            'required': True, # This parameter is required
            'type': 'string'  # The type of the parameter (string in this case)
        }
    ]
})
def get_user(name):
    logger.info(json.dumps({'event': 'get_user', 'endpoint': '/user/<name>', 'name': name}))
    user = Users.query.filter_by(name=name).first()
    if user:
        logger.info(json.dumps({'event': 'user_found', 'name': user.name, 'email': user.email}))
        return jsonify({
            'name': user.name,
            'age': user.age,
            'email': user.email
            })
    logger.warning(json.dumps({'event': 'user_not_found', 'name': name}))
    return jsonify({'error': 'User not found'}), 404

@app.route('/user', methods=['POST'])
@swag_from({
    'parameters': [
        {
            'name': 'body', 'in': 'body', 'schema': {
                'type': 'object', 'properties': {
                    'name': {'type': 'string'},
                    'age': {'type': 'integer'},
                    'email': {'type': 'string'}
                },
                'required': ['name', 'age', 'email']
            }
        }
    ],
    'responses': {
        201: {'description': 'User added'}
    }
})
def add_user():
    data = request.json
    logger.info(json.dumps({'event': 'add_user', 'endpoint': '/user', 'data': data}))
    user = Users(
        name=data['name'],
        age=data['age'],
        email=data['email']
        )
    db.session.add(user)
    db.session.commit()
    logger.info(json.dumps({'event': 'user_added', 'name': user.name, 'email': user.email}))
    return jsonify({'message': 'User added'}), 201

@app.route('/user/<email>', methods=['DELETE'])
@swag_from({
    'parameters': [
        {
            'name': 'email', 'in': 'path', 'schema': {
            'type': 'string'},
            'required': True,
            'description': 'Email of the user to delete'
        }
    ],
    'responses': {
        200: {'description': 'User deleted'},
        404: {'description': 'User not found'}
    }
})
def delete_user(email):
    logger.info(json.dumps({'event': 'delete_user', 'endpoint': '/user/<email>', 'email': email}))
    user = Users.query.filter_by(email=email).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        logger.info(json.dumps({'event': 'user_deleted', 'email': email}))
        return jsonify({'message': 'User deleted'}), 200
    logger.warning(json.dumps({'event': 'user_not_found_for_deletion', 'email': email}))
    return jsonify({'error': 'User not found'}), 404

# @app.route('/delete_all_users', methods=['DELETE'])
# @swag_from({
#     'responses': {
#         200: {'description': 'All users deleted'}
#     }
# })
# def delete_all_users():
#     """
#     Delete all users.
#     :return: JSON response indicating success or failure.
#     """
#     db.session.query(Users).delete()
#     db.session.commit()
#     return jsonify({'message': 'All users deleted'}), 200
