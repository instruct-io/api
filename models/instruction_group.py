# Imports
from util.dict_obj import DictObj
from config.config import arguments
from datetime import datetime  # noqa
from typing import Any


class InstructionGroup:
    """Model class for the instruction group"""

    # Static variable declaration
    REQ_ARGS = arguments.models.instruction_group

    def __init__(self: "InstructionGroup", **kwargs: Any) -> None:
        """Constructor for an InstructionGroup instance"""

        # Check if kwargs has the minimum arguments
        for arg in InstructionGroup.REQ_ARGS.init:
            if arg not in kwargs:
                return False

        # Save info
        self.info = DictObj(kwargs)
