# Imports
from typing import Any


class DictObject(dict):
    """Dictionary object representation

    Args:
        dict (dict): Base type
    """

    def __init__(self: "DictObject", *args: Any, **kwargs: Any) -> None:
        """Initialization of the parsed dictionary

        Args:
            self (DictObject): DictObject type
        """
        dict.__init__(self, *args, **kwargs)

    def __getattr__(self: "DictObject", name: str) -> Any:
        """Get the value of the reference key

        Args:
            self (DictObject): DictObject type
            name (str): Reference key

        Returns:
            Any: The value of the referenced key
        """
        return self[name]

    def __setattr__(self: "DictObject", name: str, val: Any) -> Any:
        """Set or create the value of the key

        Args:
            self (DictObject): DictObject type
            name (str): Name of the key
            val (Any): Value for the key

        Returns:
            Any: The value of the referenced key
        """
        self[name] = val

    def __delattr__(self: "DictObject", name: str) -> None:
        """_summary_

        Args:
            self (DictObject): DictObject type
            name (str): Name of the key to delete
        """
        del self[name]


def DictObj(config: dict) -> DictObject:
    """Dictionary object wrapper

    Args:
        config (dict): Dictionary to convert into object

    Returns:
        DictObject: Dictionary object representation
    """

    # Return requested information
    if isinstance(config, dict):
        result = DictObject()
        for key in config:
            result[key] = DictObj(config[key])
        return result
    else:
        return config
