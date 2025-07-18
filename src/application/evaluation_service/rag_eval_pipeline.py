import asyncio
import weave
import config as cfg
import logging
import os
import statistics as stats
from llama_index.llms.bedrock import Bedrock
from llama_index.core.evaluation import (
    FaithfulnessEvaluator,
    RelevancyEvaluator,
    CorrectnessEvaluator,
)

from async_rag_pipeline import AsyncRagPipeline

logger = logging.getLogger("ragpipeline")
logging.basicConfig(level=logging.INFO)


class RagEvalPipeline:
    def __init__(self, eval_gold_qa, model_provider):
        self.rag_pipe = AsyncRagPipeline(model_provider=model_provider)
        self.eval_gold_qa = eval_gold_qa
        self.model_provider = model_provider

    @staticmethod
    def set_llm_judge():
        llm_model_id = cfg.app.eval.llm_model_id
        region_name = cfg.app.eval.region
        context_size = cfg.app.eval.context_size
        temperature = cfg.app.eval.temperature
        aws_session_token = os.environ["AWS_BEARER_TOKEN_BEDROCK"]

        llm_judge = Bedrock(
            model=llm_model_id,
            region_name=region_name,
            aws_session_token=aws_session_token,
            temperature=temperature,
            context_size=context_size,
        )
        return llm_judge

    @weave.op()
    def correctness_evaluator(query: str, ground_truth: str, output: dict):
        llm_judge = RagEvalPipeline.set_llm_judge()
        evaluator = CorrectnessEvaluator(llm=llm_judge)
        result = evaluator.evaluate(
            query=query, reference=ground_truth, response=output["response"]
        )
        return {"correctness": float(result.score)}

    @weave.op()
    def relevancy_evaluator(query: str, ground_truth: str, output: dict):
        llm_judge = RagEvalPipeline.set_llm_judge()
        evaluator = RelevancyEvaluator(llm=llm_judge)
        eval_source_results = [
            evaluator.evaluate(
                query=query, contexts=[context], response=output["response"]
            )
            for context in output["contexts"]
        ]
        eval_source_result = [
            1 if result.passing else 0 for result in eval_source_results
        ]
        return {"relevancy": stats.mean(eval_source_result)}

    @weave.op()
    def faithfullness_evaluator(query: str, ground_truth: str, output: dict):
        llm_judge = RagEvalPipeline.set_llm_judge()
        evaluator = FaithfulnessEvaluator(llm=llm_judge)
        result = evaluator.evaluate_response(response=output["full_response"])
        return {"faithfullness": 1 if result.passing else 0}

    def evaluate(self):
        scorers = [
            self.correctness_evaluator,
            self.relevancy_evaluator,
            self.faithfullness_evaluator,
        ]
        evaluation = weave.Evaluation(dataset=self.eval_gold_qa, scorers=scorers)
        eval_full_results = asyncio.run(evaluation.evaluate(self.rag_pipe))
        return eval_full_results
