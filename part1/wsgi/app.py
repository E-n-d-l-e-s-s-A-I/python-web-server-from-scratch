import time

from flask import Flask, jsonify, request

from .server import WSGIServer

app = Flask("app")


@app.route("/ping")
def ping():
    return "pong"


@app.route("/sleep")
def sleep():
    time.sleep(0.5)
    return "pong"


@app.route("/page", methods=["POST"])
def submit():
    data = request.json
    name = data.get("name", "Unknown")
    return jsonify({"message": f"Hello, {name}!"})


if __name__ == "__main__":
    server = WSGIServer("0.0.0.0", 9999, app)
    server.serve_forever()
