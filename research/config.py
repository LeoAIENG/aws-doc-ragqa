import dotenv
import pandas as pd
import warnings
from itertools import starmap
from pathlib import Path
from types import SimpleNamespace
from typing import NoReturn
from utils import convert_dict_to_namespace, load_yaml, process_paths

dotenv.load_dotenv()

base_path = Path().cwd()
config_path = base_path / 'config'

def set_paths(config: SimpleNamespace) -> SimpleNamespace:
    paths = getattr(config, 'path')
    config_path = process_paths(paths, base_path)
    setattr(config, 'path', config_path)
    return config

def set_credentials(config: SimpleNamespace) -> NoReturn:
    pass

def set_globals(config: SimpleNamespace) -> NoReturn:
    for key, value in config.__dict__.items():
        globals()[key] = value

def set_notebook_config(config: SimpleNamespace) -> NoReturn:
    # Pandas Config
    pandas_config = [tuple(pdc) for pdc in config.nb.pandas._tuple]
    pandas_config += [tuple([pdc[0], lambda x: pdc[1] % x]) for pdc in config.nb.pandas._lambda]
    list(starmap(pd.set_option, pandas_config))

    # Warnings Config
    warnings.simplefilter(action='ignore', category=FutureWarning)
    warnings.filterwarnings('ignore')


def load_config() -> NoReturn:
    config = {
        path.stem: load_yaml(path)
        for path in config_path.glob('*.yaml')
    }
    config = convert_dict_to_namespace(config)
    config = set_paths(config)
    set_globals(config)
    set_notebook_config(config)
    return config

config = load_config()