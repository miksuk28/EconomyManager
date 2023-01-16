from functools import wraps
from flask import jsonify, request
from jsonschema import validate, ValidationError
from users import UsersManagement
import users_exceptions

users = UsersManagement()

def validate_json(schema, *args, **kwargs):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            json_data = request.get_json()

            if json_data == {}:
                return jsonify({"error": "No JSON body", "status": 400, "message": "JSON body is missing", "displayMessage": False}), 400
            
            try:
                validate(instance=json_data, schema=schema)

            except ValidationError as e:
                return jsonify({
                        "message": "JSON Validation error. Please check the docs",
                        "error": e.message,
                        "expectedSchema": schema,
                        "status": 400
                    }), 400

            return f(*args, **kwargs)
        return wrapper
    return decorator


def authenticate(*args, **kwargs):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = request.headers.get("X-Auth-Token")
            if token in ("", None):
                return jsonify({"error": "Missing X-Auth-Token header containing authentication token", "status": 400}), 400

            try:
                session = users.authenticate(token)

            except users_exceptions.InvalidToken:
                return jsonify({
                    "error": "Token is invalid. Please try signing in again",
                    "message": "Your authentication token is either expired or incorrect. Please try signing in again",
                    "displayMessage": True,
                    "status": 403
                }), 403

            return f(session=session, *args, **kwargs)
        return wrapper
    return decorator