# Flask related libraries and  blueprints(s)
from . import register, refresh, login, who_am_i, signout
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)

# Grab base MVC related modules for endpoints
from controllers.users import UserControl
from ._base import (
    token_required,
    param_check,
    error_handler,
)

# Miscellaneous imports
from pprint import pprint  # noqa
from typing import Tuple

#
#   CREATE OPERATIONS
#   region
#


@register.route("/register/", methods=["POST"])
@error_handler
@param_check
def register_endpoint(
    first_name: str, last_name: str, email: str, password: str
) -> Tuple[dict, int]:
    """Endpoint to handle registering users

    Args:
        first_name (str): First name of the user
        last_name (str): Last name of the user
        email (str): Email of the new user
        password (str): Password of the new user


    Returns:
        Tuple[dict, int]: Return the response of the endpoint
    """

    # Get the user's instance based on the given information
    result = UserControl.register_user(**locals())

    # Return response data
    return result, (200 if result.status == "success" else 400)


@refresh.route("/refresh/", methods=["POST"])
@jwt_required(refresh=True)
@error_handler
@param_check
def refresh_endpoint() -> Tuple[dict, int]:
    """Endpoint to handle the refresh of users' authentication

    Args:
        refresh_token (str): Refresh token for JWT refresh

    Returns:
        Tuple[dict, int]: Return the response of the endpoint
    """

    # Create a new access token
    new_token = create_access_token(identity=get_jwt_identity())

    # Return the new token
    return {"access_token": new_token}, 200


@login.route("/login/", methods=["POST"])
@error_handler
@param_check
def login_endpoint(email: str, password: str) -> Tuple[dict, int]:
    """Endpoint to handle the login of users into the application


    Args:
        email (str): Email of the user trying to login
        password (str): Password attempt

    Returns:
        Tuple[dict, int]: Return the response of the endpoint
    """

    # Get the user's instance based on the given information
    result = UserControl.login(**locals())

    # If the response data results in an error, return 400
    # and error message
    if result.status != "success":
        return result, 400

    # Create refresh and access token
    identity = {
        "email": result.message.info.email,
        "_id": result.message.info._id,
    }
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)

    # Return access and refresh tokens
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }, 200


#   endregion

#
#   READ OPERATIONS
#   region
#


@who_am_i.route("/who_am_i/", methods=["POST"])
@token_required
@error_handler
@param_check
def who_am_i_endpoint(_id: str) -> Tuple[dict, int]:
    """Endpoint to get the user's credentials

    Args:
        _id (str): User ID of the caller

    Returns:
        Tuple[dict, int]: Return the response of the endpoint
    """

    # Get the user based on the ID
    result = UserControl.get_user(_id)
    content = result.message.get_generic_info()

    # Return the results of the database query
    return content, (200 if result.status == "success" else 400)


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


@signout.route("/signout/", methods=["POST"])
@token_required
@error_handler
@param_check
def signout_endpoint(
    access_token: str, refresh_token: str, _id: str
) -> Tuple[dict, int]:
    """Sign Out Handling

    Args:
        access_token (str): Access token to trash
        refresh_token (str): Refresh token to trash
        _id (str): User ID of the caller

    Returns:
        Tuple[dict, int]: Return the response of the endpoint
    """

    # Get the user's instance based on the given information
    result = UserControl.handle_jwt_blacklisting(access_token, refresh_token)

    # Return response data
    return result, (200 if result.status == "success" else 400)


#   endregion
