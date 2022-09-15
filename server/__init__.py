import os.path
import random
import uuid
from dataclasses import dataclass, asdict
from time import time
from typing import Dict, Optional

import torch
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from torch.nn import functional as F
from transformers import T5Config, T5ForConditionalGeneration, RobertaTokenizer
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
CORS(app)


@dataclass
class Explanation:
    explanation: str
    score: float


@dataclass
class ModelData:
    name: str
    file: str


@dataclass
class ModelNames:
    Bugsplainer: ModelData = ModelData('Bugsplainer', '262.finetune-sbt-random-512-64-16-60m')
    Bugsplainer220M: ModelData = ModelData('Bugsplainer 220M', '268.finetune-sbt-random-512-64-16-220m')
    FineTunedCodeT5: ModelData = ModelData('FineTuned Code T5', '251.finetune-patch-sbt1-large-512-64-16-60m')


model_names = ModelNames()


@app.route('/models', methods=['GET'])
def get_model_names():
    models = [model['name'] for model in asdict(model_names).values()]
    return jsonify(models=models)


@app.route('/explain', methods=['POST'])
def explain():
    request_data: Dict = request.json
    code = request_data.get('code')
    start = request_data.get('start')
    end = request_data.get('end')
    model = request_data.get('model')
    num_explanations = request_data.get('num_explanations')

    if model == model_names.FineTunedCodeT5.name:
        explanations = _get_explanations_from_fine_tuned_CodeT5(
            code, start, end, num_explanations
        )
    else:
        explanations = [Explanation(
            f'This is an explanation from {model} for line {start} to {end}',
            1 - (random.random() * 0.1),
        )]

    return jsonify(model=model, explanations=explanations)


MODEL_DIR = 'server/models'
device = torch.device('cuda')


def _get_explanations_from_fine_tuned_CodeT5(
        code: str, start: int, end: int, num_explanations: Optional[int] = None,
):
    tokenizer = RobertaTokenizer.from_pretrained('Salesforce/codet5-base')
    config = T5Config.from_pretrained(os.path.join(MODEL_DIR, 'config_60m.json'))
    model_path = os.path.join(
        MODEL_DIR, ModelNames.FineTunedCodeT5.file, 'output', 'checkpoint-best-bleu',
    )
    model: T5ForConditionalGeneration = T5ForConditionalGeneration.from_pretrained(
        model_path, config=config,
    )
    model.to(device)
    model.eval()

    code_lines = [
        line for i, line in enumerate(code.splitlines(), 1)
        if start <= i <= end
    ]

    buggy_code = '\n'.join(code_lines)
    source_str = f"finetune patch: {buggy_code}"
    source_ids = tokenizer.encode(
        source_str, max_length=512, padding='max_length', truncation=True,
    )
    source_tensor = torch.tensor([source_ids], dtype=torch.long, device=device)
    source_mask = source_tensor.ne(tokenizer.pad_token_id)

    outputs = model.generate(
        inputs=source_tensor,
        attention_mask=source_mask,
        early_stopping=True,
        num_beams=10,
        num_return_sequences=num_explanations or 3,
        output_scores=True,
        return_dict_in_generate=True,
    )

    explanations = [
        tokenizer.decode(seq, skip_special_tokens=True, clean_up_tokenization_spaces=True)
        for seq in outputs.sequences
    ]

    scores = F.softmax(outputs.sequences_scores, dim=0).tolist()
    return [
        Explanation(*param) for param in zip(explanations, scores)
    ]


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
