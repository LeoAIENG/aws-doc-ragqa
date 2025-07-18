import dotenv
from pathlib import Path
from types import SimpleNamespace
from typing import NoReturn
from utils import load_obj, convert_dict_to_namespace, process_paths

dotenv.load_dotenv()

base_path = Path().cwd()
config_path = base_path / "config"


def set_paths(config: SimpleNamespace) -> SimpleNamespace:
    """
    Update the 'path' attribute in the config with processed paths.
    """
    paths = getattr(config, "path")
    config_path = process_paths(paths, base_path)
    setattr(config, "path", config_path)
    return config


def set_credentials(config: SimpleNamespace) -> NoReturn:
    """
    Placeholder for setting credentials in the config.
    """
    pass


def set_globals(config: SimpleNamespace) -> None:
    """
    Set config attributes as global variables.
    """
    for key, value in config.__dict__.items():
        globals()[key] = value


def load_config() -> SimpleNamespace:
    """
    Load configuration files, process paths, and set globals.
    """
    config = {path.stem: load_obj(path) for path in config_path.glob("*.yaml")}
    config = convert_dict_to_namespace(config)
    config = set_paths(config)
    set_globals(config)
    return config


config = load_config()
