from typing import Dict
from llama_index.embeddings.bedrock import BedrockEmbedding
from llama_index.llms.bedrock import Bedrock

from utils.logger import setup_logger

logger = setup_logger(__name__)


def initialize_bedrock(llm_config: Dict):
    model_name = llm_config["model"]
    logger.info(f"Setting AWS LLM: {model_name}")
    return Bedrock(**llm_config)


def initialize_bedrock_embed(embed_config: Dict):
    model_name = embed_config["model_name"]
    logger.info(f"Setting AWS Embedding: {model_name}")
    return BedrockEmbedding(**embed_config)
