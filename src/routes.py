from flask import request, jsonify
from app import app, db
from models import Users
from flasgger.utils import swag_from

@app.route('/users', methods=['GET'])
@swag_from({
    'responses': {200: {'description': 'List of users', 'schema': {'type': 'array', 'items': {'type': 'object'}}}}
})
def get_all_users():
    users = Users.query.all()  # Query all users
    if users:
        # Convert the user objects to dictionaries and return them as JSON
        return jsonify([{'name': user.name, 'age': user.age, 'email': user.email} for user in users])
    return jsonify({'error': 'No users found'}), 404

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
    user = Users.query.filter_by(name=name).first()
    if user:
        return jsonify({'name': user.name, 'age': user.age, 'email': user.email})
    return jsonify({'error': 'User not found'}), 404

@app.route('/user', methods=['POST'])
@swag_from({
    'parameters': [
        {'name': 'body', 'in': 'body', 'schema': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'age': {'type': 'integer'}}}}
    ],
    'responses': {201: {'description': 'User added'}}
})
def add_user():
    data = request.json
    user = Users(name=data['name'], age=data['age'], email=data['email'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User added'}), 201
