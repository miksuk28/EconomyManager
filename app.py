from flask import Flask, jsonify, request, abort
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


#### POST: Login with username and password, to receive token
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
        }), 200 # OK

    except (users_exceptions.IncorrectCredentials, users_exceptions.UserDoesNotExist) as error:
        return jsonify({
            "message":          "Wrong credentials. Please check if the username and password is correct",
            "error":            "Bad credentials",
            "status":           403,
            "displayMessage":   True
        }), 403 # Forbidden
    
    except Exception as error:
        abort(500, session, error)



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
        }), 201 # Created

    except psycopg2.errors.DatetimeFieldOverflow:
        return jsonify({
            "message":          "Date is out of range. Please check if it follows the format YYYY-MM-DD",
            "error":            "Date is out of range YYYY-MM-DD",
            "displayMessage":   True
        }), 400 # Bad Request

    except economy_exceptions.DuplicateItems:
        return jsonify({
            "message":          "The receipt contains duplicate items. Please remove the duplicate(s)",
            "error":            "Receipt has duplicate products",
            "status":           409,
            "displayMessage":   True
        }), 409 # Bad Request

    except Exception as error:
        session["original_exception"] = error
        abort(500, session)


### GET: Get receipt summary for user
@app.route("/receipts", methods=["GET"])
@authenticate()
def get_all_receipts(session):
    return jsonify(economy.get_receipts(session["user_id"]))



### GET: Get items in receipt for user, by receipt_id
@app.route("/receipts/<int:id>", methods=["GET"])
@authenticate()
def get_receipt(id, session):
    items, receipt_info = economy.get_receipt_items(
        user_id=session["user_id"],
        receipt_id=id
    )

    if not items:
        return jsonify({
            "message":          f"No receipt with the id {id} exists",
            "error":            f"Receipt with id {id} does not exist",
            "status":           404,
            "displayMessage2":  True
        }), 404
    
    else:
        return jsonify({
            "message":          f"Returned receipt with id {id}",
            "total_items":      receipt_info["total_items"],
            "unique_items":     receipt_info["unique_items"],
            "total":            receipt_info["total"],
            "date":             receipt_info["date"],
            "files":            receipt_info["files"],
            "products":         items
        }), 200


#### ERROR HANDLERS
# 500 - Internal Server Error
@app.errorhandler(500)
def internal_server_error(session):
    print(f"\n\nSESSION DATA: {session.description['original_exception']}\n\n")
    return jsonify({
        "message":          "An internal server error has occured. If this error persist, please contact the admin",
        "error":            "500 Internal Server Error",
        "status":           500,
        "displayMessage":   True
    }), 500 # Internal Server Error


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)