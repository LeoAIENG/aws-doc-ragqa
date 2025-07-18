import weave
import config as cfg
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.prompts import RichPromptTemplate

from llm.base import set_model
from vector_database.base import set_vector_store
from utils.logger import setup_logger

weave.init(cfg.app.weave.project)
logger = setup_logger(__name__)


class RagPipeline(weave.Model):
    model_provider: str = "aws"
    model_name: str = "claude-3-haiku"
    model_type: str = "llm"
    vector_db: str = "qdrant"
    temperature: float = 0.2
    similarity_top_k: int = 5
    context_size: int = 200000
    async_mode: bool = cfg.app.async_mode

    def set_models(self) -> None:
        models = set_model(
            model_provider=self.model_provider,
            model_name=self.model_name,
            model_type=self.model_type,
        )
        Settings.llm = models["llm"]
        Settings.embed_model = models["embed_model"]

    def get_template(self):
        prompt_template = cfg.templates.prompt.doc_qa
        return RichPromptTemplate(prompt_template)

    def get_index(self):
        vector_store = set_vector_store(
            vector_db=self.vector_db,
            model_provider=self.model_provider,
            async_mode=self.async_mode,
        )
        index = VectorStoreIndex.from_vector_store(vector_store)
        return index

    def setup_query_engine(self):
        self.set_models()
        index = self.get_index()
        prompt_template = self.get_template()
        return index.as_query_engine(
            similarity_top_k=self.similarity_top_k,
            text_qa_template=prompt_template,
        )

    async def aquery(self, query: str):
        query_engine = self.setup_query_engine()
        response = await query_engine.aquery(query)
        return response

    def get_contexts(self, response) -> list:
        source_nodes = response.source_nodes
        return [node.get_content() for node in source_nodes]

    def get_source_documents(self, response) -> list:
        source_nodes = response.source_nodes
        return set([node.metadata.get("file_name", "N/A") for node in source_nodes])

    @weave.op()
    async def predict(self, query: str):
        response = await self.aquery(query)
        source_documents = self.get_source_documents(response)
        return {"response": response.response, "source_documents": source_documents}

    @weave.op()
    async def eval_apredict(self, query: str):
        response = await self.aquery(query)
        contexts = self.get_contexts(response)
        return {
            "full_response": response,
            "response": response.response,
            "contexts": contexts,
        }


rag_pipe = RagPipeline(
    model_provider=cfg.app.model.provider,
    model_name=cfg.app.model.name,
    model_type=cfg.app.model.type,
    vector_db=cfg.app.vector_db.name,
    temperature=cfg.model.gen_params.temperature,
    similarity_top_k=cfg.vector_db.retriever.similarity_top_k,
    async_mode=cfg.app.async_mode,
)
