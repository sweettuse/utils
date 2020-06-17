import json

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/slack/emojify')
def emojify():
    with open('/tmp/flask_test', 'w') as f:
        json.dump(request.json, f, indent=4)
    return 'emojify'
