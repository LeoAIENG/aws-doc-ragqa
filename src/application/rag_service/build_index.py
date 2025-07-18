import config as cfg
import pandas as pd
import config as cfg
from pathlib import Path
from llama_index.core import (
	VectorStoreIndex,
	SimpleDirectoryReader,
	StorageContext,
	Settings,
)
from llama_index.core.node_parser import MarkdownNodeParser
from pathlib import Path
from utils.logger import setup_logger
from utils.file_utils import load_obj
from typing import Any, Dict, List, Union

from llm.base import set_model
from vector_database.base import set_vector_store
from vector_database.qdrant_vector_db_client import (
    initialize_qdrant, check_collection_exists, get_qdrant_url, get_collection_name
)

logger = setup_logger(__name__)

category_files_df = load_obj(cfg.path.data.interim / "category_files_df_v1.pickle", as_df=True)

def get_category(df: pd.DataFrame, path: Union[Path, str]) -> str:
	"""
	Retrieve the category for a given file path from the dataframe.

	Args:
		df (pd.DataFrame): DataFrame containing 'path' and 'category' columns.
		path (Union[Path, str]): The file path to look up.

	Returns:
		str: The category associated with the file path.

	Raises:
		IndexError: If the path is not found in the DataFrame.
	"""
	category = df[df.path == Path(path)]["category"].values[0]
	logger.debug(f"Category for {path}: {category}")
	return category

def get_metadata(file_path: Union[Path, str]) -> Dict[str, str]:
	"""
	Generate metadata dictionary for a given file path.

	Args:
		file_path (Union[Path, str]): The file path.

	Returns:
		Dict[str, str]: Metadata including file name and category.
	"""
	file_path = Path(file_path)
	meta = {"file_name": file_path.name, "category": get_category(category_files_df, file_path)}
	logger.debug(f"Metadata for {file_path}: {meta}")
	return meta

def get_nodes(df: pd.DataFrame) -> List[Any]:
	"""
	Parse markdown documents into nodes using the provided DataFrame.

	Args:
		df (pd.DataFrame): DataFrame with a 'path' column.

	Returns:
		List[Any]: List of parsed nodes.
	"""
	logger.info("Loading documents and parsing nodes...")
	paths = df.path.tolist()
	docs = SimpleDirectoryReader(
		input_files=paths,
		file_metadata=get_metadata
	).load_data()
	parser = MarkdownNodeParser()
	nodes = parser.get_nodes_from_documents(docs)
	logger.info(f"Parsed {len(nodes)} nodes from {len(paths)} documents.")
	return nodes

def set_models(model_provider: str, model_name: str, model_type: str) -> None:
	models = set_model(
		model_provider=model_provider,
		model_name=model_name,
		model_type=model_type
	)
	Settings.llm = models["llm"]
	Settings.embed_model = models["embed_model"]

def build_index(
	model_provider: str,
	model_name: str,
	model_type: str,
	vector_db: str,
	force_reindex: bool = False
) -> None:
	"""
	Build or load a VectorStoreIndex from Qdrant, setting up the LLM and embedding model.

	Args:
		vector_store (QdrantVectorStore): The vector store instance.
		nodes (List[Any]): List of nodes to index.
		model_provider (str, optional): Model provider, "aws" or "gemini". Defaults to "aws".
		force_reindex (bool, optional): If True, force reindexing. Defaults to False.

	Returns:
		VectorStoreIndex: The index instance.
	"""
	
	logger.info(f"Building index with model provider: {model_provider}, force_reindex={force_reindex}")
	nodes = get_nodes(category_files_df)
	url = get_qdrant_url()
	vector_db_client = initialize_qdrant(url=url)
	collection_name = get_collection_name(model_provider)
	collections_exists = check_collection_exists(client=vector_db_client, collection_name=collection_name)
	vector_store = set_vector_store(vector_db=vector_db, model_provider=model_provider, async_mode=False)

	# Setup LLM llamaindex settings
	set_models(
		model_name=model_name,
		model_provider=model_provider,
		model_type=model_type
	)

	if not force_reindex and collections_exists:
		logger.info("Index already exists. Loading from Qdrant.")
	else:
		logger.info("Building a new index in Qdrant.")
		storage_context = StorageContext.from_defaults(
			vector_store=vector_store,
		)
		index = VectorStoreIndex(
			nodes, 
			storage_context=storage_context,
			show_progress=True,
		)

