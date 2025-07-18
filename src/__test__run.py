import sys
import asyncio
from pathlib import Path
src_path = (Path.cwd() / "src").as_posix()
sys.path.append(src_path)

import config as cfg
from application.rag_service.rag_pipeline import rag_pipe

# rag_pipe = RagPipeline(
#     model_provider=cfg.app.model.provider,
# 	model_name=cfg.app.model.name,
# 	model_type=cfg.app.model.type,
# 	vector_db=cfg.app.vector_db.name,
# 	temperature=cfg.model.gen_params.temperature,
# 	similarity_top_k=cfg.vector_db.retriever.similarity_top_k,
#     async_mode=cfg.app.async_mode
# )

query = "What is AWS?"

result = asyncio.run(rag_pipe.predict(query))

print(result)