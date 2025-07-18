import qdrant_client
import os
import config as cfg
from llama_index.vector_stores.qdrant import QdrantVectorStore

from utils.logger import setup_logger

logger = setup_logger(__name__)


def initialize_qdrant(url: str) -> qdrant_client:
    logger.info(f"Connecting to Qdrant at {url}")
    return qdrant_client.QdrantClient(url=url)


def initialize_async_qdrant(url: str) -> qdrant_client:
    logger.info(f"Connecting to Qdrant at {url}")
    return qdrant_client.AsyncQdrantClient(url=url)
    # return qdrant_client.AsyncQdrantClient(url=url)


def qdrant_vector_store(
    client: qdrant_client,
    collection_name: str,
) -> QdrantVectorStore:
    logger.info(f"Connecting to Qdrant to collection: {collection_name}")
    vector_store = QdrantVectorStore(client=client, collection_name=collection_name)
    return vector_store


def qdrant_async_vector_store(
    client: qdrant_client, collection_name: str
) -> QdrantVectorStore:
    logger.info(f"Connecting to Qdrant to collection: {collection_name}")
    return QdrantVectorStore(aclient=client, collection_name=collection_name)


def check_collection_exists(client: qdrant_client, collection_name: str) -> bool:
    collection_exists = client.collection_exists(collection_name=collection_name)
    if collection_exists:
        logger.info(f"Collection '{collection_name}' exists!")
    else:
        logger.info(f"Collection '{collection_name}' does not exist!")
    return collection_exists


def get_qdrant_url() -> str:
    qdrant_host = os.getenv("QDRANT_HOST", cfg.vector_db.qdrant.host)
    qdrant_port = os.getenv("QDRANT_PORT", cfg.vector_db.qdrant.port)
    url = f"{qdrant_host}:{qdrant_port}"
    logger.info(f"QUADRANT URL: {url}")
    return url


def get_collection_name(model_provider: str) -> str:
    collection_name = getattr(cfg.vector_db.qdrant.collection, model_provider)
    return collection_name
