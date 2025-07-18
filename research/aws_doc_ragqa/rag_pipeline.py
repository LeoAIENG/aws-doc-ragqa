import logging
import os

import config as cfg
from dotenv import load_dotenv
from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.prompts import RichPromptTemplate
from llama_index.embeddings.bedrock import BedrockEmbedding
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.bedrock import Bedrock
from llama_index.llms.gemini import Gemini
from llama_index.vector_stores.qdrant import QdrantVectorStore
import qdrant_client
import weave

load_dotenv()
logger = logging.getLogger("ragpipeline")
logging.basicConfig(level=logging.INFO)

weave.init("aws-doc-ragqa-demo")


class RagPipeline(weave.Model):
    temperature: float = 0.1
    similarity_top_k: int = 5
    prompt_template: str = cfg.templates.prompt.aws_doc_qa
    model_provider: str = "aws"

    def set_llm_aws(self) -> None:
        """
        Initialize Bedrock LLM and Embedding model for AWS and set them in Settings.
        """
        llm_model_id = cfg.app.aws.llm_model_id
        embed_model_id = cfg.app.aws.embedding_model_id
        region_name = cfg.app.aws.region
        aws_session_token = os.environ["AWS_BEARER_TOKEN_BEDROCK"]

        logger.info(f"Setting AWS LLM: {llm_model_id}, Embedding: {embed_model_id}")
        llm = Bedrock(
            model=llm_model_id,
            region_name=region_name,
            aws_session_token=aws_session_token,
            temperature=self.temperature,
        )
        embed_model = BedrockEmbedding(
            model_name=embed_model_id, region_name=region_name, aws_session_token=aws_session_token
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

            if (llm_model == cfg.app.aws.llm_model_id) and (
                embed_model == cfg.app.aws.embedding_model_id
            ):
                return "aws"
            elif (llm_model == cfg.app.gemini.llm_model_id) and (
                embed_model == cfg.app.gemini.embedding_model_id
            ):
                return "gemini"
            else:
                return None
        except:
            return None

    def set_model_provider(self) -> None:
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
                logger.warning(
                    f"Unknown model provider: {self.model_provider}. Defaulting to AWS."
                )
                self.set_llm_aws()
        else:
            logger.info("The Model provider is already set.")

    def get_template(self):
        return RichPromptTemplate(self.prompt_template)

    def qdrant_vector_store(self) -> QdrantVectorStore:
        """
        Create a QdrantVectorStore instance using configuration.

        Returns:
                QdrantVectorStore: The vector store instance.
        """
        collection_name = getattr(cfg.app.qdrant.collection, self.model_provider)
        url = cfg.app.qdrant.url

        logger.info(f"Connecting to Qdrant at {url}, collection: {collection_name}")
        client = qdrant_client.QdrantClient(url=url)
        vector_store = QdrantVectorStore(client=client, collection_name=collection_name)
        return vector_store

    def get_index(self):
        logger.info("Preparing to get index...")
        self.set_model_provider()
        vector_store = self.qdrant_vector_store()
        index = VectorStoreIndex.from_vector_store(vector_store)
        return index

    def get_retriever(self):
        index = self.get_index()
        prompt_template = self.get_template()

        return index.as_retriever(
            similarity_top_k=self.similarity_top_k,
            text_qa_template=prompt_template,
        )

    def get_query_engine(self):
        index = self.get_index()
        prompt_template = self.get_template()

        return index.as_query_engine(
            similarity_top_k=self.similarity_top_k,
            text_qa_template=prompt_template,
        )

    def get_response(self, query: str):
        query_engine = self.get_query_engine()
        response = query_engine.query(query)
        return response

    def retrieve_nodes(self, query: str):
        retriever = self.get_retriever()
        nodes = retriever.retrieve(query)
        return nodes

    @weave.op()
    def predict(self, query: str):
        query_engine = self.get_query_engine()
        response = query_engine.query(query)
        return {"response": response.response}
