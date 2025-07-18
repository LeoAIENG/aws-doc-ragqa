import config as cfg
import os

from llm.bedrock_client import initialize_bedrock, initialize_bedrock_embed
from llm.gemini_client import initialize_gemini, initialize_gemini_embed
from utils.model_utils import model_config

def set_model(model_provider: str, model_name: str, model_type: str):
    llm_cfg, embed_cfg = model_config(model_provider, model_name, model_type)
    match model_provider:
        case "aws":
            aws_session_token = os.environ.get("AWS_BEARER_TOKEN_BEDROCK", None)
            if aws_session_token:
                llm_cfg.update({"aws_session_token": aws_session_token})
                embed_cfg.update({"aws_session_token": aws_session_token})
            llm = initialize_bedrock(llm_cfg)
            embed_model = initialize_bedrock_embed(embed_cfg)
        case "gemini":
            llm = initialize_gemini(llm_cfg)
            embed_model = initialize_gemini_embed(embed_cfg)
        case _:
            raise Exception("The model provider is not available.")
    return {"llm": llm, "embed_model": embed_model}