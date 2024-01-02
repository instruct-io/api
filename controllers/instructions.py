# Imports
from models.instruction_group import InstructionGroup
from util.dict_obj import DictObj
from ._base import Controller
from typing import Any
from pprint import pprint  # noqa
import uuid


class InstructionControl(Controller):
    """Class that demonstrates the control logic of Instruction(s) model(s)"""

    @staticmethod
    @Controller.return_dict_obj
    def create_instruction_group(name: str, _id: str) -> DictObj:
        """Create a new instruction group

        Args:
            name (str): Name of the new instruction group
            _id (str): ID of the owner of the new instruction group

        Returns:
            DictObj: Result of the query
        """

        # Prep data to be inserted
        insert = {}
        insert["_id"] = str(uuid.uuid4().hex)
        insert["name"] = name
        insert["owner"] = _id
        insert["steps"] = [
            {
                "name": f"{name} Step #1",
                "description": "Lorem Ipsum Dolor Sit Amet",
            }
        ]
        print(insert)

        # Insert into the collection
        Controller.INSTRUCTION_GROUP_COL.insert_one(insert)

        # Return a statement
        return Controller.success("Instruction group created")

    @staticmethod
    @Controller.return_dict_obj
    def get_instruction_group(id: str) -> DictObj:
        """Controller to handle the search of an instruction group

        Args:
            id (str): ID of the instruction group to return

        Returns:
            DictObj: Result of the search
        """

        # Get the instruction group information
        group = Controller.INSTRUCTION_GROUP_COL.find_one({"_id": id})

        # Return the instruction group
        if not group:
            return Controller.success({})
        return Controller.success(InstructionGroup(**group))

    @staticmethod
    @Controller.return_dict_obj
    def get_users_instruction_groups(_id: str) -> DictObj:
        """Controller to get the user's instruction groups

        Args:
            _id (str): ID of the owner requesting their instruction groups

        Returns:
            DictObj: Result of the query
        """

        # Get the user's instruction groups
        groups = Controller.INSTRUCTION_GROUP_COL.find({"owner": _id})
        groups = [InstructionGroup(**item) for item in groups]

        # Return list of owned instruction groups
        return Controller.success(groups)

    @staticmethod
    @Controller.return_dict_obj
    def get_checkpoint(id: str, _id: str) -> DictObj:
        """Get the user's checkpoint while doing an instruction group

        Args:
            id (str): ID of the instruction group
            _id (str): ID of the user requesting the checkpoint

        Returns:
            DictObj: Indexed positioning of the user's checkpoint
        """

        # Get the user's checkpoint information
        pos = Controller.CHECKPOINT_COL.find_one({"ig_id": id, "user_id": _id})

        # Return the result
        if pos is None:
            return Controller.success(0)
        else:
            return Controller.success(pos["position"])

    @staticmethod
    @Controller.return_dict_obj
    def update_instruction_group(id: str, _id: str, **kwargs: Any) -> DictObj:
        """Controller to update an instruction group

        Args:
            id (str): ID of the instruction group to update
            _id (str): ID of the user requesting the update

        Returns:
            DictObj: Result of the operation
        """

        # Check if the update request is possible with the given id and user id
        res = Controller.INSTRUCTION_GROUP_COL.find_one(
            {"_id": id, "owner": _id}
        )
        if not res:
            return Controller.error("You cannot edit this instruction group")

        # Ensure that any empty kwargs are not sent for updating
        copy = kwargs.copy()
        for i in copy:
            if not kwargs[i]:
                del kwargs[i]

        # If steps is in the remaining kwargs, ensure that it has the proper
        # structure
        if "steps" in kwargs:
            for i in kwargs["steps"]:
                if "name" not in i or "description" not in i:
                    return Controller.error(
                        "Improper update of the instruction group"
                    )

        # If all else is good, update the instruction group
        Controller.INSTRUCTION_GROUP_COL.update_one(
            {"_id": id}, {"$set": kwargs}
        )

        # Return result
        return Controller.success("Update is a success")

    @staticmethod
    @Controller.return_dict_obj
    def save_checkpoint(id: str, _id: str, pos: int) -> DictObj:
        """Update a user's checkpoint on an instruction group

        Args:
            id (str): ID of the instruction group that the user is on
            _id (str): ID of the user
            pos (int): Numerical position of the user in the playthrough

        Returns:
            DictObj: Status of the update
        """

        # Replace one and upsert to save checkpoint
        Controller.CHECKPOINT_COL.replace_one(
            {"ig_id": id, "user_id": _id},
            {"ig_id": id, "user_id": _id, "position": pos},
            upsert=True,
        )

        # Send updated status
        return Controller.success("Checkpoint saved")

    @staticmethod
    @Controller.return_dict_obj
    def delete_instruction_group(id: str, _id: str) -> DictObj:
        """Controller to delete an instruction group

        Args:
            id (str): ID of the instruction group to delete
            _id (str): ID of the user requesting the deletion

        Returns:
            DictObj: Result of the deletion
        """

        # Check if the user has ownership of the instruction group
        res = Controller.INSTRUCTION_GROUP_COL.find_one(
            {"_id": id, "owner": _id}
        )
        if not res:
            return Controller.error(
                "You do not have access to this instruction group"
            )

        # If so, delete the instruction group
        Controller.INSTRUCTION_GROUP_COL.delete_one({"_id": id, "owner": _id})

        # Return success message
        return Controller.success("Deletion complete")
