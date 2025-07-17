import weave
import qdrant_client
import logging
import os
import asyncio
import nest_asyncio
import config as cfg
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.prompts import RichPromptTemplate
from llama_index.llms.bedrock import Bedrock
from llama_index.embeddings.bedrock import BedrockEmbedding
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.gemini import Gemini
from llama_index.core.schema import MetadataMode
from llama_index.core.evaluation import (
    FaithfulnessEvaluator,
    RelevancyEvaluator,
    CorrectnessEvaluator,
    RetrieverEvaluator,
)
from typing import NoReturn

logger = logging.getLogger("ragpipeline")
logging.basicConfig(level=logging.INFO)

weave.init("aws-doc-ragqa-demo")

class AsyncRagPipeline(weave.Model):
	prompt_template: str = cfg.templates.prompt.doc_qa
	model_provider: str = "aws"
	temperature: float = None
	similarity_top_k: int = None
	context_size: int = None


	def set_configuration(self):
		model_cfg = getattr(cfg.app, self.model_provider)
		if hasattr(model_cfg, "similarity_top_k"):
			self.similarity_top_k = model_cfg.similarity_top_k
		if hasattr(model_cfg, "temperature"):
			self.temperature = model_cfg.temperature
		if hasattr(model_cfg, "context_size"):
			self.context_size = model_cfg.context_size

	def set_llm_aws(self) -> None:
		"""
		Initialize Bedrock LLM and Embedding model for AWS and set them in Settings.
		"""
		llm_model_id = cfg.app.aws.llm_model_id
		embed_model_id = cfg.app.aws.embedding_model_id
		region_name = cfg.app.aws.region
		context_size = cfg.app.aws.context_size
		aws_session_token = os.environ["AWS_BEARER_TOKEN_BEDROCK"]
		
		logger.info(f"Setting AWS LLM: {llm_model_id}, Embedding: {embed_model_id}")
		llm = Bedrock(
			model=llm_model_id,
			region_name=region_name,
			aws_session_token=aws_session_token,
			temperature=self.temperature,
			context_size=context_size
		)
		embed_model = BedrockEmbedding(
			model_name=embed_model_id,
			region_name=region_name,
			aws_session_token=aws_session_token
		)
		Settings.llm = llm
		Settings.embed_model = embed_model

	def set_llm_gemini(self) -> None:
		"""
		Initialize Gemini LLM and Embedding model and set them in Settings.
		"""
		llm_model_id = cfg.app.gemini.llm_model_id
		embed_model_id = cfg.app.gemini.embedding_model_id
		
		logger.info(f"Setting Gemini LLM: {llm_model_id}, Embedding: {embed_model_id}")
		llm = Gemini(model=llm_model_id)
		embed_model = GeminiEmbedding(model_name=embed_model_id)
		Settings.llm = llm
		Settings.embed_model = embed_model

	def get_model_provider(self):
		try:
			llm_model = Settings.llm.model
			embed_model = Settings.embed_model.model_name
			
			if (llm_model == cfg.app.aws.llm_model_id) and (embed_model == cfg.app.aws.embedding_model_id):
				return "aws"
			elif (llm_model == cfg.app.gemini.llm_model_id) and (embed_model == cfg.app.gemini.embedding_model_id):
				return "gemini"
			else:
					return None
		except:
			return None

		
	def set_model_provider(self) -> None:
		self.set_configuration()
		cur_model_provider = self.get_model_provider()
		if self.model_provider != cur_model_provider:
			logger.info(f"The current model is: {cur_model_provider}")
			if self.model_provider == "aws":
				logger.info("Setting AWS Model...")
				self.set_llm_aws()
			elif self.model_provider == "gemini":
				logger.info("Setting Gemini Model...")
				self.set_llm_gemini()
			else:
				logger.warning(f"Unknown model provider: {self.model_provider}. Defaulting to AWS.")
				self.set_llm_aws()
		else:
			logger.info("The Model provider is already set.")
		

	async def get_template(self):
		return RichPromptTemplate(self.prompt_template)
	
	async def qdrant_vector_store(self) -> QdrantVectorStore:
		"""
		Create a QdrantVectorStore instance using configuration.
		
		Returns:
			QdrantVectorStore: The vector store instance.
		"""
		collection_name = getattr(cfg.app.qdrant.collection, self.model_provider)
		url = cfg.app.qdrant.url
		
		logger.info(f"Connecting to Qdrant at {url}, collection: {collection_name}")
		client = qdrant_client.AsyncQdrantClient(url=url)
		vector_store = QdrantVectorStore(
			aclient=client, 
			collection_name=collection_name
		)
		return vector_store
	
	async def get_index(self):
		logger.info("Preparing to get index...")
		self.set_model_provider()
		vector_store = await self.qdrant_vector_store()
		index = VectorStoreIndex.from_vector_store(vector_store)
		return index
	
	def get_retriever(self):
		index = self.get_index()
		prompt_template = self.get_template()

		return index.as_retriever(
			similarity_top_k=self.similarity_top_k,
			text_qa_template=prompt_template,
		)

	async def get_query_engine(self):
		index = await self.get_index()
		prompt_template = await self.get_template()

		return index.as_query_engine(
			similarity_top_k=self.similarity_top_k,
			text_qa_template=prompt_template,
		)
	
	async def get_response(self, query: str):
		query_engine = await self.get_query_engine()
		response = await query_engine.aquery(query)
		return response
	
	async def get_contexts(self, response) -> list:
		source_nodes = response.source_nodes
		return [node.get_content() for node in source_nodes]
	
	async def retrieve_nodes(self, query: str):
		retriever = self.get_retriever()
		nodes = await retriever.aretrieve(query)
		return nodes

	@weave.op()
	async def predict(self, query: str):
		response = await self.get_response(query)
		contexts = await self.get_contexts(response)
		return {
			"full_response": response,
			"response": response.response,
			"contexts": contexts
		}