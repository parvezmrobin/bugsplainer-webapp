import os.path
import uuid
from dataclasses import dataclass, asdict
from time import time
from typing import Dict, Optional, List

import pandas as pd
import torch
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from torch.nn import functional as F
from transformers import T5Config, T5ForConditionalGeneration, RobertaTokenizer
from werkzeug.exceptions import HTTPException

from .Bugsplainer import Bugsplainer

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
        large = model == model_names.Bugsplainer220M.name
        explanations = _get_explanations_from_Bugsplainer(
            code, start, end,
            config_path=os.path.join(MODEL_DIR, 'config_220m.json' if large else 'config_60m.json'),
            num_explanations=num_explanations,
            large=large
        )

    return jsonify(model=model, explanations=explanations)


@app.route('/experimental/files', methods=['GET'])
def get_experimental_files():
    df: pd.DataFrame = pd.read_csv('./data/test-sbt-random-finetune.csv', usecols=['repo', 'path'])
    filenames: pd.Series = df['repo'].str.replace('.', '/', regex=False) + '/' + df['path']
    filenames = filenames[filenames.str.len() < 50]
    return jsonify(files=filenames[-100:].sort_values().tolist())


@app.route('/experimental/file')
def get_experimental_file_content():
    filename = request.values['path']
    app.logger.info('filename: %s', filename)
    df: pd.DataFrame = pd.read_csv(
        './data/test-sbt-random-finetune.csv',
        usecols=['repo', 'path', 'commit_message', 'content', 'start', 'end'],
    )
    filename_parts = filename.split('/')
    repo = '.'.join(filename_parts[:2])
    path = '/'.join(filename_parts[2:])
    df = df[(df['repo'] == repo) & (df['path'] == path)]

    return jsonify(
        content=df.iloc[0]['content'],
        start=df['start'].tolist(),
        end=df['end'].tolist(),
        commit_message=df['commit_message'].tolist(),
    )


def group_recursively(filename_parts: List[List[str]], level=0) -> Dict[str, List]:
    keywords = set(
        filename_part[level] for filename_part in filename_parts
        if len(filename_part) - 1 > level
    )
    group = {
        key: [] for key in keywords
    }
    group['files'] = []
    for filename_part in filename_parts:
        dirname = filename_part[level]
        if dirname in group:
            group[dirname].append(filename_part)
        else:
            group['files'].append(filename_part)

    for dirname, files in group.items():
        if dirname != 'files':
            group[dirname] = group_recursively(files, level=level + 1)

    return group


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


def _get_explanations_from_Bugsplainer(
        code: str, start: int, end: int, config_path: str, num_explanations: Optional[int] = None, large=False,
):
    model_file = ModelNames.Bugsplainer220M.file if large else ModelNames.Bugsplainer.file
    model_path = os.path.join(
        MODEL_DIR, model_file, 'output', 'checkpoint-best-bleu',
    )
    bugsplainer = Bugsplainer(max_length=512, config_path=config_path, model_path=model_path)
    sbt = Bugsplainer.make_sbt_from_span(code, start, end)
    explanation = bugsplainer.explain(sbt, num_explanations=num_explanations or 3)
    return [
        Explanation(*param) for param in zip(explanation.explanations, explanation.scores)
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
