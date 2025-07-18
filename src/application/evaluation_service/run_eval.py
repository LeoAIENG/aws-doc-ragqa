import nest_asyncio

nest_asyncio.apply()

import sys
import config as cfg
from dotenv import load_dotenv
from rag_eval_pipeline import RagEvalPipeline
from utils import load_obj

load_dotenv()

model_provider = "aws"
if len(sys.argv) > 1:
    if sys.argv[1] == "--gemini":
        model_provider = "gemini"

eval_gold_qa = load_obj(cfg.path.data.processed / "evaluation_gold_qa_dataset.pkl")

rag_eval_pipe = RagEvalPipeline(
    eval_gold_qa=eval_gold_qa, model_provider=model_provider
)
rag_eval_pipe.evaluate()
