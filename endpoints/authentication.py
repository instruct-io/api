# Import blueprints(s)
from . import register

# Flask related libraries
from flask import request

# Grab base MVC related modules for endpoints
from controllers._base import Controller
from ._base import arg_check, error_handler, client_error, success, ARGS

# Miscellaneous imports
from util.dict_obj import DictObj

# Extract supabase connection from base controller
supabase = Controller.supabase

#
#   CREATE OPERATIONS
#   region
#


@register.route("/register/", methods=["POST"])
@arg_check(ARGS.authentication.register)
@error_handler
def register_endpoint(**kwargs):
    """Endpoint to handle the registration of users into the application"""

    # Extract data from the JSON body
    data = DictObj(request.get_json())

    # Send error if email or password is not provided
    if not data.email or not data.password:
        return client_error("Email or password not provided")

    # Create new user
    response = DictObj(supabase.auth.sign_up(data.email, data.password))

    # Check if the registration was successful
    if response.get("error"):
        return client_error(response.error.message)

    # Return success if all is good
    return success(response.get("data"))


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
