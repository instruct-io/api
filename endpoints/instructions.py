# Import blueprint(s)
from . import create_instruction_group, get_instruction_group_instructions

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
from ._base import arg_check, error_handler, ARGS

# Miscellaneous imports
from util.dict_obj import DictObj

#
#   CREATE OPERATIONS
#   region
#


@create_instruction_group.route("/create_instruction_group/", methods=["POST"])
@arg_check(ARGS.instructions.create_instruction_group)
@error_handler
def create_instruction_group_endpoint(**kwargs):
    """Endpoint to handle the creation of a new instruction group"""

    # Extract data from the JSON body
    data = DictObj(request.get_json())

    # Create a new instruction group
    res = InstructionControl.create_instruction_group(**data)

    # Return the result of the new creation of an instruction group
    return res


#   endregion

#
#   READ OPERATIONS
#   region
#


@get_instruction_group_instructions.route(
    "/get_instruction_group_instructions/", methods=["POST"]
)
@arg_check(ARGS.instructions.get_instruction_group_instructions)
@error_handler
def get_instruction_group_instructions_endpoint(**kwargs):
    """Endpoint to handle the creation of a new instruction group"""

    # Extract data from the JSON body
    data = DictObj(request.get_json())

    # Create a new instruction group
    res = InstructionControl.get_instruction_group_instructions(data.ig_uid)

    # Return the result of the new creation of an instruction group
    return res


#   endregion

#
#   UPDATE OPERATIONS
#   region
#

#   ! N/A

#   endregion

#
#   DELETE OPERATIONS
#   region
#

#   ! N/A

#   endregion
