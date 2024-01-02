# Imports
from util.dict_obj import DictObj
from typing import List


class InstructionGroup:
    """Instruction Group class model"""

    def __init__(
        self: "InstructionGroup",
        _id: str,
        name: str,
        owner: str,
        steps: List[dict],
    ) -> None:
        """Constructor for the Instruction Group class

        Args:
            self (InstructionGroup): Current class type
            _id (str): ID of the instruction group
            name (str): Name of the instruction group
            owner (str): ID of the owner of the instruction group
            steps (List[dict]): List of steps of the instruction group
        """

        # Save info
        self.info = DictObj({k: v for k, v in locals().items() if k != "self"})
        self.info.update(self.info.pop("kwargs", {}))
