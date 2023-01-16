from flask import Flask, jsonify, request
from economy import EconomyManager
from users import UsersManagement
from wrappers import validate_json, authenticate
import economy_exceptions
import users_exceptions
import json_schemas

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


economy = EconomyManager()
users = UsersManagement()


@app.route("/hello", methods=["GET"])
def index():
    return "Hello, World"


@app.route("/login", methods=["POST"])
@validate_json(json_schemas.login)
def login():
    body = request.get_json()
    try:
        token = users.login(
            username=body["username"],
            password=body["password"]
        )

        return jsonify({"token": token, "status": 200, "message": "Authenticated. Use the token as a header in future requests", "displayMessage": False})

    except users_exceptions.IncorrectCredentials:
        return jsonify({"message": "Wrong credentials. Access denied", "error": "Wrong credentials", "status": 403, "displayMessage": True}), 403


@app.route("/receipts", methods=["POST"])
@validate_json(json_schemas.create_receipt)
@authenticate()
def create_receipt(session):
    body = request.get_json()
    print(body)

    return jsonify({"message": "OK"}), 200


@app.route("/receipts", methods=["GET"])
@authenticate()
def get_all_receipts(session):
    return jsonify(economy.get_receipts(session["user_id"]))


@app.route("/receipts/<int:id>", methods=["GET"])
@authenticate()
def get_receipt(id, session):
    return jsonify(economy.get_receipt_items(
        user_id=session["user_id"],
        receipt_id=id
    ))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)