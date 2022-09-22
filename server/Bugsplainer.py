from typing import NamedTuple, List

from torch import cuda
from torch import device, tensor, long
from torch.nn import functional as F
from transformers import T5Config, RobertaTokenizer, T5ForConditionalGeneration

assert cuda.is_available(), 'CUDA is not available'


class Explanation(NamedTuple):
  explanations: List[str]
  scores: List[int]


class Bugsplainer:
  def __init__(self, *, max_length: int, config_path: str, model_path: str):
    self.max_length = max_length
    self.device = device('cuda')
    config = T5Config.from_pretrained(config_path)
    self.tokenizer = RobertaTokenizer.from_pretrained('Salesforce/codet5-base')
    self.model: T5ForConditionalGeneration = T5ForConditionalGeneration.from_pretrained(model_path, config=config)
    self.model.to(self.device)
    self.model.eval()

  @staticmethod
  def make_sbt_from_diff(code: str, diff: str):
    if len(diff.split()) > 100:
      raise Exception('You are using base version of Bugsplainer which under-performs '
                      'when the diff contains more than 100 whitespace-tokens. '
                      'Contact the author to use large version of Bugsplainer.')
    from .StructureSuperimposer import StructureSuperImposer

    structure_superimposer = StructureSuperImposer.from_diff(code, diff)
    return structure_superimposer.to_bracketed_notation(source_only=True)

  @staticmethod
  def make_sbt_from_span(code: str, start: int, end: int):
    from .StructureSuperimposer import StructureSuperImposer

    structure_superimposer = StructureSuperImposer.from_source_code(code, start, end)
    return structure_superimposer.to_bracketed_notation(source_only=True)

  def explain(self, sbt: str, num_explanations=10):
    source_str = f"finetune sbt-random: {sbt}"
    source_ids = self.tokenizer.encode(source_str, max_length=self.max_length, padding='max_length', truncation=True)
    source_tensor = tensor([source_ids], dtype=long, device=self.device)
    source_mask = source_tensor.ne(self.tokenizer.pad_token_id)

    outputs = self.model.generate(
      inputs=source_tensor,
      attention_mask=source_mask,
      early_stopping=True,
      num_beams=10,
      num_return_sequences=num_explanations,
      output_scores=True,
      return_dict_in_generate=True,
    )

    explanations = [
      self.tokenizer.decode(seq, skip_special_tokens=True, clean_up_tokenization_spaces=True)
      for seq in outputs.sequences
    ]

    return Explanation(
      explanations,
      F.softmax(outputs.sequences_scores, dim=0).tolist(),
    )
