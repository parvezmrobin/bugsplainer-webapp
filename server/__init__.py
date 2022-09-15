import random
import re
import uuid
from dataclasses import dataclass, asdict
from time import time
from typing import Dict

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
CORS(app)


@dataclass
class ModelNames:
    Bugsplainer: str = '262.finetune-sbt-random-512-64-16-60m'
    Bugsplainer220M: str = '268.finetune-sbt-random-512-64-16-220m'
    FineTunedCodeT5: str = '251.finetune-patch-sbt1-large-512-64-16-60m'


model_names = ModelNames()


@app.route('/models', methods=['GET'])
def get_model_names():
    next_ch_cap_re = re.compile('(?<=[a-z])(?=[A-Z0-9])')
    models = [' '.join(next_ch_cap_re.split(model)) for model in asdict(model_names).keys()]
    return jsonify(models=models)


@app.route('/explain', methods=['POST'])
def explain():
    request_data: Dict = request.json
    code = request_data.get('code')
    start = request_data.get('start')
    end = request_data.get('end')
    model = request_data.get('model')

    explanations = [{
        'score': 1 - (random.random() * 0.1),
        'explanation': f'This is an explanation from {model} for line {start} to {end}'
    }]

    return jsonify(model=model, explanations=explanations)


@app.before_request
def set_req_ids():
    request.environ['id'] = uuid.uuid4()
    request.environ['created'] = time()


@app.after_request
def send_req_ids(response: Response):
    response = {
        # in OPTIONS requests, response.json is None
        **(response.json if response.json else {}),
        'id': request.environ['id'],
        'created': request.environ['created'],
        'completed': time(),
    }

    return jsonify(response)


@app.errorhandler(Exception)
def handle_exception(e: Exception):
    app.logger.error('Error: %s', e)

    status_code = 500
    if isinstance(e, HTTPException):
        status_code = e.code
    return jsonify(message=repr(e)), status_code
