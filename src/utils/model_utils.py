import config as cfg
from utils.file_utils import convert_namespace_to_dict


def model_config(model_provider: str, model_name: str, model_type: str):
    model_cfg = cfg.model
    gen_cfg = model_cfg.gen_params
    gen_cfg = convert_namespace_to_dict(gen_cfg)

    # Model Provider Config
    model_provider_cfg = getattr(model_cfg, model_provider)

    # LLM Model Config
    llm_cfg = getattr(model_provider_cfg, model_type)
    llm_cfg = getattr(llm_cfg, model_name)
    llm_cfg = convert_namespace_to_dict(llm_cfg)
    print(type(llm_cfg))
    llm_cfg.update(gen_cfg)

    # Embedding Model Config
    embed_cfg = model_provider_cfg.embed
    embed_cfg = convert_namespace_to_dict(embed_cfg)

    return llm_cfg, embed_cfg
