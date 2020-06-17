import json

from flask import Flask, jsonify, request

app = Flask(__name__)



@app.route('/slack/emojify', methods=['POST'])
def emojify():
    print(request.get_data().decode())
    print(request.form)
    # print(str(request.get_json(force=True)))
    # with open('/tmp/flask_test', 'a') as f:
        # f.write(str(request.get_json(force=True)))
    return ':cushparrot:'
