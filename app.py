from flask import Flask, jsonify, request

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


@app.route("/", methods=["GET"])
def index():
    return "Hello, World"


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)