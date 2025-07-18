from typing import Dict
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.gemini import Gemini

from utils.logger import setup_logger

logger = setup_logger(__name__)


def initialize_gemini(llm_config: Dict):
    model_name = llm_config["model"]
    logger.info(f"Setting Gemini LLM: {model_name}")
    return Gemini(**llm_config)


def initialize_gemini_embed(embed_config: Dict):
    model_name = embed_config["model_name"]
    logger.info(f"Setting Gemini Embedding: {model_name}")
    return GeminiEmbedding(**embed_config)
