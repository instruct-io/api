# Flask related libraries and  blueprints(s)
from . import (
    create_instruction_group,
    get_instruction_group,
    get_users_instruction_groups,
    update_instruction_group,
    get_checkpoint,
    save_checkpoint,
    delete_instruction_group,
)

# Grab base MVC related modules for endpoints
from controllers.instructions import InstructionControl
from ._base import (
    token_required,
    param_check,
    error_handler,
)


# Miscellaneous imports
from typing import Tuple, List
from pprint import pprint  # noqa


#
#   CREATE OPERATIONS
#   region
#


@create_instruction_group.route("/create_instruction_group/", methods=["POST"])
@token_required
@error_handler
@param_check
def create_instruction_group_endpoint(name: str, _id: str) -> Tuple[dict, int]:
    """Endpoint to handle the creation of a new instruction group

    Args:
        name (str): Name of the instruction group
        _id (str): ID of the user

    Returns:
        Tuple[dict, int]: Return the response of the endpoint
    """
    # Create a new instruction group
    res = InstructionControl.create_instruction_group(**locals())

    # Return the result of the new creation of an instruction group
    return res, 400 if res.status == "error" else 200


#   endregion

#
#   READ OPERATIONS
#   region
#


@get_instruction_group.route("/get_instruction_group/", methods=["POST"])
@error_handler
@param_check
def get_instruction_group_endpoint(id: str) -> Tuple[dict, int]:
    """Endpoint to handle the read of an instruction group

    Args:
        id (str): ID of the instruction group

    Returns:
        Tuple[dict, int]: Return the response of the endpoint
    """

    # Get instructions from instruction group
    res = InstructionControl.get_instruction_group(id)
    if res.message:
        res.message = res.message.info

    # Return the result
    return res, 400 if res.status == "error" else 200


@get_users_instruction_groups.route(
    "/get_users_instruction_groups/", methods=["POST"]
)
@token_required
@error_handler
@param_check
def get_users_instruction_groups_endpoint(_id: str) -> Tuple[dict, int]:
    """Endpoint to handle the retrieval of a user's instruction groups

    Args:
        _id (str): ID of the user

    Returns:
        Tuple[dict, int]: Return the response of the endpoint
    """

    # Get user's instruction groups
    res = InstructionControl.get_users_instruction_groups(**locals())
    if res.message:
        res.message = [item.info for item in res.message]

    # Return the result
    return res, 400 if res.status == "error" else 200


@get_checkpoint.route("/get_checkpoint/", methods=["POST"])
@token_required
@error_handler
@param_check
def get_checkpoint_endpoint(id: str, _id: str) -> Tuple[dict, int]:
    """Get the position where the user was last of

    Args:
        id (str): Instruction group's ID
        _id (str): User's ID

    Returns:
        Tuple[dict, int]: Return the response of the endpoint
    """

    # Get instructions from instruction group
    res = InstructionControl.get_checkpoint(**locals())

    # Return the result
    return res, 400 if res.status == "error" else 200


#   endregion

#
#   UPDATE OPERATIONS
#   region
#


@update_instruction_group.route("/update_instruction_group/", methods=["POST"])
@token_required
@error_handler
@param_check
def update_instruction_group_endpoint(
    id: str, _id: str, name: str = "", steps: List[dict] = []
) -> Tuple[dict, int]:
    """Endpoint to handle the updating of an instruction group

    Args:
        id (str): ID of the instruction group to update
        _id (str): ID of the user updating the instruction group
        name (str): Updated name of the instruction
        steps (List[dict]): Updated list of steps for the instruction group

    Returns:
        Tuple[dict, int]: Return the response of the endpoint
    """

    # Update the instruction group
    res = InstructionControl.update_instruction_group(**locals())

    # Return the result
    return res, 400 if res.status == "error" else 200


@save_checkpoint.route("/save_checkpoint/", methods=["POST"])
@token_required
@error_handler
@param_check
def save_checkpoint_endpoint(id: str, _id: str, pos: int) -> Tuple[dict, int]:
    """Endpoint to save a checkpoint

    Args:
        id (str): ID of the instruction group to save the check point
        _id (str): ID of the user for the check point
        pos (int): Position of the user saving a check point

    Returns:
        Tuple[dict, int]: Return the response of the endpoint
    """

    # Save the user's checkpoint
    res = InstructionControl.save_checkpoint(**locals())

    # Return the result
    return res, 400 if res.status == "error" else 200


#   endregion

#
#   DELETE OPERATIONS
#   region
#


@delete_instruction_group.route("/delete_instruction_group/", methods=["POST"])
@token_required
@error_handler
@param_check
def delete_instruction_group_endpoint(id: str, _id: str) -> Tuple[dict, int]:
    """Endpoint to handle the deletion of an instruction group

    Args:
        id (str): ID of the instruction group to delete
        _id (str): ID of the user requesting the deletion

    Returns:
        Tuple[dict, int]: Return the response of the endpoint
    """

    # Get instructions from instruction group
    res = InstructionControl.delete_instruction_group(**locals())

    # Return the result
    return res, 400 if res.status == "error" else 200


#   endregion
