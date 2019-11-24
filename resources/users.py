import models
from flask import request, jsonify, Blueprint
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from playhouse.shortcuts import model_to_dict

user = Blueprint('users', 'user')


@user.route('/register', methods=['POST'])
def register():
    payload = request.get_json()
    payload['email'].lower()
    try:
        models.User.get(models.User.email == payload['email'])
        return jsonify(
            data={},
            status={
                "code": 401,
                "message": "A user with that email already exists."
            }
        ), 401
    except models.DoesNotExist:
        payload['password'] = generate_password_hash(payload['password'])
        new_user = models.User.create(**payload)
        login_user(new_user)
        new_user_dict = model_to_dict(new_user)
        del new_user_dict['password']
        return jsonify(
            data=new_user_dict,
            status={
                "code": 201,
                "message": f"Success - {new_user_dict['username']} registered"
            }
        ), 201


@user.route('/login', methods=['POST'])
def login():
    payload = request.get_json()
    try:
        user = models.User.get(models.User.email == payload['email'])
        user_dict = model_to_dict(user)
        if check_password_hash(user_dict['password'], payload['password']):
            login_user(user)
            user_dict.pop('password')
            return jsonify(
                data=user_dict,
                status={
                    "code": 200,
                    "message": f"{user_dict['username']} logged in."
                }
            )
    except models.DoesNotExist:
        return jsonify(
            data={},
            status={
                "code": 401,
                "message": "Credentials couldn't be verified."
            }
        ), 401


@user.route('/logout', methods=['GET'])
@login_required
def logout():
    username = model_to_dict(current_user)['username']
    logout_user()
    return jsonify(
        data={},
        status={
            "code": 200,
            "message": f"{username} successfully logged out."
        }
    )
