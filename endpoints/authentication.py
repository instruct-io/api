# Import blueprints(s)
from . import register, login, refresh

# Flask related libraries
from flask import request

# Grab base MVC related modules for endpoints
from controllers._base import Controller
from ._base import arg_check, error_handler, client_error, success, ARGS

# Miscellaneous imports
from util.dict_obj import DictObj
from pprint import pprint  # noqa

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
    supabase.auth.sign_up({"email": data.email, "password": data.password})

    # Return success if all is good
    return success("Registration complete. Check your Email.")


@refresh.route("/refresh/", methods=["POST"])
@arg_check(ARGS.authentication.refresh)
@error_handler
def refresh_endpoint(**kwargs):
    """Endpoint to handle the refresh of users' authentication"""

    # Extract data from the JSON body
    data = DictObj(request.get_json())

    # Create new user
    user = supabase.auth.refresh_session(data["refresh"])

    # Return success if all is good
    return success(
        {
            "access": user.session.access_token,
            "refresh": user.session.refresh_token,
            "expires": user.session.expires_in,
        }
    )


#   endregion

#
#   READ OPERATIONS
#   region
#


@login.route("/login/", methods=["POST"])
@arg_check(ARGS.authentication.login)
@error_handler
def login_endpoint(**kwargs):
    """Endpoint to handle the login of users into the application"""

    # Extract data from the JSON body
    data = DictObj(request.get_json())

    # Send error if email or password is not provided
    if not data.email or not data.password:
        return client_error("Email or password not provided")

    # Login the user
    user = supabase.auth.sign_in_with_password(
        {"email": data.email, "password": data.password}
    )

    # Return success if all is good
    return success(
        {
            "access": user.session.access_token,
            "refresh": user.session.refresh_token,
            "expires": user.session.expires_in,
        }
    )


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
