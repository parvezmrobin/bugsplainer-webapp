import sys
import uuid
from dataclasses import dataclass, asdict
from time import time

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
CORS(app)


@dataclass
class ModelNames:
    Bugsplainer: str = 'Bugsplainer'
    Bugsplainer220M: str = 'Bugsplainer 220M'
    FineTunedCodeT5: str = 'Fine-Tuned CodeT5'


model_names = ModelNames()


@app.route('/models', methods=['GET'])
def get_model_names():
    return jsonify(models=asdict(model_names))


@app.before_request
def set_req_ids():
    request.environ['id'] = uuid.uuid4()
    request.environ['created'] = time()


@app.after_request
def send_req_ids(response: Response):
    response = {
        **response.json,
        'id': request.environ['id'],
        'created': request.environ['created'],
        'completed': time(),
    }

    return jsonify(response)


@app.errorhandler(Exception)
def handle_exception(e: Exception):
    print(e, sys.stderr)

    status_code = 500
    if isinstance(e, HTTPException):
        status_code = e.code
    return jsonify(message=repr(e)), status_code
