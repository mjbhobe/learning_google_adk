from google.adk.models.lite_llm import LiteLlm
from stock_analysis_adk.config import DEFAULT_MODEL


def make_model():
    return LiteLlm(model=DEFAULT_MODEL)
