# Import blueprint(s)
from . import (
    create_instruction_group,
    get_instructions,
    get_instruction_groups,
    update_instructions,
)

# Import JWT related libraries
from flask_jwt_extended import (  # noqa
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)

# Flask related libraries
from flask import request

# Grab base MVC related modules for endpoints
from controllers.instructions import InstructionControl
from ._base import arg_check, error_handler, token_required, ARGS

# Miscellaneous imports
from util.dict_obj import DictObj

#
#   CREATE OPERATIONS
#   region
#


@create_instruction_group.route("/create_instruction_group/", methods=["POST"])
@arg_check(ARGS.instructions.create_instruction_group)
@token_required
@error_handler
def create_instruction_group_endpoint(**kwargs):
    """Endpoint to handle the creation of a new instruction group"""

    # Extract data from the JSON body
    data = DictObj(request.get_json())
    data.access_token = kwargs["access_token"]

    # Create a new instruction group
    res = InstructionControl.create_instruction_group(**data)

    # Return the result of the new creation of an instruction group
    return res, 400 if res.status == "error" else 200


#   endregion

#
#   READ OPERATIONS
#   region
#


@get_instructions.route("/get_instructions/", methods=["POST"])
@arg_check(ARGS.instructions.get_instructions)
@error_handler
def get_instructions_endpoint(**kwargs):
    """Endpoint to handle the read of instructions from instruction group"""

    # Extract data from the JSON body
    data = DictObj(request.get_json())

    # Get instructions from instruction group
    res = InstructionControl.get_instructions(data.ig_uid)

    # Return the result of the new creation of an instruction group
    return res, 400 if res.status == "error" else 200


@get_instruction_groups.route("/get_instruction_groups/", methods=["POST"])
@token_required
@error_handler
def get_instruction_groups_endpoint(**kwargs):
    """Endpoint to handle the retrieval of a user's instruction groups"""

    # Get user's instruction groups
    res = InstructionControl.get_instruction_groups(kwargs["access_token"])

    # Return the result of the new creation of an instruction group
    return res, 400 if res.status == "error" else 200


#   endregion

#
#   UPDATE OPERATIONS
#   region
#


@update_instructions.route("/update_instructions/", methods=["POST"])
@arg_check(ARGS.instructions.update_instructions)
@error_handler
def update_instructions_endpoint(**kwargs):
    """Endpoint to handle the update of an instruction group"""

    # Extract data from the JSON body
    data = DictObj(request.get_json())

    # Update an instruction group
    res = InstructionControl.update_instructions(
        data.ig_uid, data.instructions
    )

    # Return the result of the new creation of an instruction group
    return res, 400 if res.status == "error" else 200


#   endregion

#
#   DELETE OPERATIONS
#   region
#

#   ! N/A

#   endregion
