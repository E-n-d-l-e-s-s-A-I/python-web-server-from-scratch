import logging
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


@app.route("/post", methods=["POST"])
def submit():
    data = request.json
    name = data.get("name", "Unknown")
    return jsonify({"message": f"Hello, {name}!"})


@app.route("/page")
def page():
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Simple Page</title>
        </head>
        <body>
            <h1>Hello, world!</h1>
            <p>This is a simple HTTP page from Flask.</p>
        </body>
    </html>
    """


if __name__ == "__main__":
    server = WSGIServer("0.0.0.0", 9999, app)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    server.serve_forever()
