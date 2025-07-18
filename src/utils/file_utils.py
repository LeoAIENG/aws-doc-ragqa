import pandas as pd
import pickle as pkl
import joblib
import json
import re
import yaml
from typing import Any
from pathlib import PosixPath
from types import SimpleNamespace
from typing import Dict


class REqual(str):
    """
    A string subclass that overrides the __eq__ method to allow regex pattern matching.

    When compared with another string using ==, this class will return True if the
    string fully matches the given regex pattern.

    Example:
        >>> REqual("foo123") == r"foo\d+"
        True
    """

    def __eq__(self, pattern):
        return re.fullmatch(pattern, self)


def save_obj(obj: Any, path: PosixPath, mkdir: bool = False, **kwargs) -> None:
    """
    Save an object to a file at the specified path.

    The saving method is determined by the file extension:
        - For pandas DataFrames: supports csv, parquet, xls, xlsx, orc, sql, pickle.
        - For pickle files: uses pickle.
        - For joblib files: uses joblib.
        - For json files: uses json.

    Args:
        obj (Any): The object to save.
        path (PosixPath): The file path to save the object to.
        mkdir (bool, optional): If True, create parent directories if they do not exist. Default is False.
        **kwargs: Additional keyword arguments passed to the underlying save function.

    Raises:
        AttributeError: If the save method for the DataFrame is not found.
    """
    path.parent.mkdir(parents=True, exist_ok=True)  # Create the folder if necessary
    suf = path.suffix[1:]  # Filename Suffix
    if isinstance(obj, pd.DataFrame):  # Pandas DataFrame
        if suf != "pickle":
            kwargs["index"] = 0
        method = f"to_{suf}" if suf not in ("xlsx", "xls") else "to_excel"
        try:
            exec = getattr(obj, method)
            exec(path, **kwargs)
        except AttributeError as e:
            raise AttributeError(e)
    else:
        match REqual(suf):
            case "pkl|pickle":  # Pickle File
                path.write_bytes(pkl.dumps(obj, **kwargs))
            case "joblib":  # Joblib File
                joblib.dump(obj, path, *kwargs)
            case "json":
                path.write_text(json.dumps(obj, **kwargs))
            case _:
                pass


def load_obj(path: PosixPath, **kwargs) -> Any:
    """
    Load an object from a file at the specified path.

    The loading method is determined by the file extension:
        - For pandas DataFrames: supports csv, parquet, xls, xlsx, orc, sql.
        - For pickle files: uses pickle.
        - For joblib files: uses joblib.
        - For json/jsonl files: uses json or pandas.
        - For yaml/yml files: uses PyYAML.

    Special kwargs:
        as_df (bool): If True, load as a pandas DataFrame (for json, jsonl, pickle).
        as_namespace (bool): If True, convert loaded yaml to a SimpleNamespace.

    Args:
        path (PosixPath): The file path to load the object from.
        **kwargs: Additional keyword arguments passed to the underlying load function.

    Returns:
        Any: The loaded object.

    Raises:
        AttributeError: If the load method for the DataFrame is not found.
    """
    suf = path.suffix[1:]  # Filename Suffix
    match REqual(suf):
        case r"csv|parquet|xls|xlsx|orc|sql":  # Pandas DataFrame
            method = f"read_{suf}" if suf not in ("xlsx", "xls") else "read_excel"
            try:
                exec = getattr(pd, method)
                return exec(path, **kwargs)
            except AttributeError as e:
                raise AttributeError(e)
        case "jsonl":
            if kwargs.get("as_df"):
                del kwargs["as_df"]
                return pd.read_json(path, lines=True, **kwargs)
            else:
                return json.loads(path.read_text(), **kwargs)
        case "json":
            if kwargs.get("as_df"):
                del kwargs["as_df"]
                return pd.read_json(path, **kwargs)
            else:
                return json.loads(path.read_text(), **kwargs)
        case "pkl|pickle":
            if kwargs.get("as_df"):
                del kwargs["as_df"]
                return pd.read_pickle(path, **kwargs)
            else:
                return pkl.loads(path.read_bytes(), **kwargs)
        case "yml|yaml":
            return yaml.safe_load(path.read_text(), **kwargs)
        case "joblib":
            return joblib.load(path, **kwargs)
        case "md":
            return path.read_text()
        case _:
            pass


def convert_dict_to_namespace(_dict: Dict) -> SimpleNamespace:
    """
    Recursively converts a dictionary into a SimpleNamespace object.

    Each key-value pair in the dictionary becomes an attribute of the resulting SimpleNamespace.
    If a value is itself a dictionary, it is recursively converted to a SimpleNamespace.
    The original dictionary is also stored as the 'config' attribute of the namespace.

    Args:
        _dict (Dict): The dictionary to convert.

    Returns:
        SimpleNamespace: The resulting namespace object.

    Raises:
        Exception: If the input is not a dictionary.
    """
    if isinstance(_dict, dict):
        namespace = SimpleNamespace()
        setattr(namespace, "config", _dict)
        for key, value in _dict.items():
            if isinstance(value, dict):
                setattr(namespace, key, convert_dict_to_namespace(value))
            else:
                setattr(namespace, key, value)
        return namespace
    else:
        raise Exception("The input must be a dictionary")
    return _dict


def convert_namespace_to_dict(namespace: SimpleNamespace) -> dict:
    """
    Recursively converts a SimpleNamespace object into a dictionary.

    Each attribute of the SimpleNamespace becomes a key-value pair in the resulting dictionary.
    If an attribute is itself a SimpleNamespace, it is recursively converted to a dictionary.
    The 'config' attribute is skipped to avoid duplication.

    Args:
        namespace (SimpleNamespace): The namespace to convert.

    Returns:
        dict: The resulting dictionary.

    Raises:
        Exception: If the input is not a SimpleNamespace.
    """
    if not isinstance(namespace, SimpleNamespace):
        raise Exception("The input must be a SimpleNamespace")
    result = {}
    for key, value in vars(namespace).items():
        if key == "config":
            continue  # Skip the 'config' attribute
        if isinstance(value, SimpleNamespace):
            result[key] = convert_namespace_to_dict(value)
        else:
            result[key] = value
    return result


def process_paths(
    paths_namespace: SimpleNamespace, base_path: PosixPath, config_path=None
):
    """
    Recursively processes a SimpleNamespace object, converting all string attributes
    (assumed to be relative paths) into absolute Paths by joining them with a base path.
    Nested SimpleNamespace objects are processed recursively.

    Args:
        paths_namespace (SimpleNamespace): The namespace object containing path strings or nested namespaces.
        base_path (Path): The base directory to join with relative path strings.
        config_path (SimpleNamespace, optional): The namespace object to populate with processed paths.
            If None, a new SimpleNamespace is created.

    Returns:
        SimpleNamespace: A new namespace object with all string paths converted to Path objects,
        and all nested namespaces processed recursively.
    """
    if config_path is None:
        config_path = SimpleNamespace()
    items = [
        (key, getattr(paths_namespace, key))
        for key in dir(paths_namespace)
        if not key.startswith("_") and not callable(getattr(paths_namespace, key))
    ]
    for key, value in items:
        if hasattr(value, "__dict__"):
            nested_namespace = SimpleNamespace()
            setattr(config_path, key, process_paths(value, base_path, nested_namespace))
        elif isinstance(value, str):
            setattr(config_path, key, base_path / value)
        else:
            setattr(config_path, key, value)
    return config_path
