
import yaml
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, Union

def convert_dict_to_namespace(_dict: Dict) -> SimpleNamespace:
    if isinstance(_dict, dict):
        namespace = SimpleNamespace()
        setattr(namespace, 'config', _dict)
        for key, value in _dict.items():
            if isinstance(value, dict):
                setattr(namespace, key, convert_dict_to_namespace(value))
            else:
                setattr(namespace, key, value)
        return namespace
    else:
        raise Exception("The input must be a dictionary")
    return _dict

def load_yaml(path: Path, namespace=False) -> Union[SimpleNamespace, Dict]:
    _dict = yaml.safe_load(path.read_text())
    return convert_dict_to_namespace(_dict) if namespace else _dict

def process_paths(paths_namespace: SimpleNamespace, base_path: Path, config_path=None):
    """Recursively process paths, handling only namespace objects"""
    
    if config_path is None:
        config_path = SimpleNamespace()
    items = [
        (key, getattr(paths_namespace, key))
        for key in dir(paths_namespace)
        if not key.startswith('_') and not callable(getattr(paths_namespace, key))
    ]
    for key, value in items:
        if hasattr(value, '__dict__'):
            nested_namespace = SimpleNamespace()
            setattr(config_path, key, process_paths(value, base_path, nested_namespace))
        elif isinstance(value, str):
            setattr(config_path, key, base_path / value)
        else:
            setattr(config_path, key, value)
    return config_path