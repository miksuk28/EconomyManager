from flask import Flask, jsonify, request
from economy import EconomyManager
from users import UsersManagement
from wrappers import validate_json, authenticate
import economy_exceptions
import users_exceptions
import json_schemas
import psycopg2.errors

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


economy = EconomyManager()
users = UsersManagement()

#### Hello World
@app.route("/hello", methods=["GET"])
def index():
    return "Hello, World"


#### Login with username and password, to receive token
@app.route("/login", methods=["POST"])
@validate_json(json_schemas.login)
def login():
    body = request.get_json()
    try:
        token = users.login(
            username=body["username"],
            password=body["password"]
        )

        return jsonify({
            "token": token,
            "status": 200,
            "message":          "Authenticated. Use the token as a header in future requests",
            "displayMessage":   False
        }), 200

    except users_exceptions.IncorrectCredentials:
        return jsonify({
            "message":          "Wrong credentials. Access denied",
            "error":            "Wrong credentials",
            "status":           403,
            "displayMessage":   True
        }), 403


#### POST: Create receipt with items
@app.route("/receipts", methods=["POST"])
@validate_json(json_schemas.create_receipt)
@authenticate()
def create_receipt(session):
    body = request.get_json()
    try:
        # Created and returns the receipt_id
        receipt_id = economy.create_receipt(session["user_id"], body["products"])
        return jsonify({
            "message":          f"Successfully created receipt with the id of {receipt_id}",
            "status":           201,
            "displayMessage":   False
        }), 201

    except psycopg2.errors.DatetimeFieldOverflow:
        return jsonify({
            "message":          "Date is out of range. Please check if it follows the format YYYY-MM-DD",
            "error":            "Date is out of range YYYY-MM-DD",
            "displayMessage":   True
        }), 400

    except economy_exceptions.DuplicateItems:
        return jsonify({
            "message":          "The receipt contains multiple products. Please remove the duplicate",
            "error":            "Receipt has duplicate products",
            "status":           409,
            "displayMessage":   True
        }), 400


### Get receipt summary for user
@app.route("/receipts", methods=["GET"])
@authenticate()
def get_all_receipts(session):
    return jsonify(economy.get_receipts(session["user_id"]))


### Get items in receipt for user, by receipt_id
@app.route("/receipts/<int:id>", methods=["GET"])
@authenticate()
def get_receipt(id, session):
    return jsonify(economy.get_receipt_items(
        user_id=session["user_id"],
        receipt_id=id
    ))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)