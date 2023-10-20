# Imports
from util.dict_obj import DictObj
from config.config import arguments
from datetime import datetime  # noqa
from typing import Any


class Example:
    """Example model class for demonstration purposes"""

    # Static variable declaration
    REQ_ARGS = arguments.models.example

    def __init__(self: "Example", **kwargs: Any) -> None:
        """Constructor for an Example instance"""

        # Check if kwargs has the minimum arguments
        for arg in Example.REQ_ARGS.init:
            if arg not in kwargs:
                return False

        # Save info
        self.info = DictObj(kwargs)

    def example_method(self: "Example", attr1: "str") -> str:
        """Method example to show how using model system is useful"""

        # Returns `{attr2} {attr1} 1234` string
        return f"{self.info.attr2} {self.info.attr1} 1234"
