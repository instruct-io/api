# Import blueprint(s)
from . import create_example

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
from models.example_ import Example  # noqa
from ._base import arg_check, error_handler, ARGS
from controllers.example_ import ExampleControl

#
#   CREATE OPERATIONS
#   region
#


@create_example.route("/create_example/", methods=["POST"])
@arg_check(ARGS.example_endpoint.create_example)
@error_handler
def create_example_endpoint(**kwargs):
    """Example create endpoint"""

    # Parse information from the call's body
    data = request.get_json()

    # Get the user's instance based on the given information
    result = ExampleControl.create_example(**data)

    # Return response data
    return result, (200 if result.status == "success" else 400)


#   endregion

#
#   READ OPERATIONS
#   region
#

#   ! N/A

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
