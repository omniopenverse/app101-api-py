from flask import request, jsonify
from app import app, db
from models import User
from flasgger.utils import swag_from

@app.route('/user/<name>', methods=['GET'])
@swag_from({
    'responses': {200: {'description': 'User age', 'schema': {'type': 'object'}}}
})
def get_user(name):
    user = User.query.filter_by(name=name).first()
    if user:
        return jsonify({'name': user.name, 'age': user.age})
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
    user = User(name=data['name'], age=data['age'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User added'}), 201
