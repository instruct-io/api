# Flask Imports
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask import Flask

# Controller Import
from controllers._base import Controller

# Miscellaneous Imports
from config.config import config
from datetime import timedelta
from typing import Any, Tuple
import os

# Endpoint imports
# region
from endpoints.authentication import (
    register,
    refresh,
    login,
    who_am_i,
    signout,
)

from endpoints.instructions import (
    create_instruction_group,
    get_instruction_group,
    get_users_instruction_groups,
    update_instruction_group,
    get_checkpoint,
    save_checkpoint,
    delete_instruction_group,
)

# endregion

#
#   FLASK APP CONFIGURATION
#   region
#

# Make app instance
app = Flask(__name__)

# Set CORS for the application
CORS(app, methods=["POST", "GET"])

# Initialize JWT functionalities
app.config["JWT_SECRET_KEY"] = config.JWT.secret
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(
    hours=config.JWT.access_expiry
)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(
    hours=config.JWT.refresh_expiry
)
jwt = JWTManager(app)


# Define the blacklist checker for JWT
@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    """Function override to check if the user's jwt information is part of
    a blacklist

    Args:
        jwt_header (dict): UNUSED - JWT header information
        jwt_payload (dict): JWT payload content

    Returns:
        bool: True if the user's JWT is in the blacklist, false if else
    """

    # Get the JWT token information
    jti = jwt_payload["jti"]

    # Check if the token is blacklisted
    query = Controller.BLACKLIST_COL.find_one({"refresh_jti": jti})

    # Return true if it is, false if not
    return query is not None


# Customize expired token message
@jwt.expired_token_loader
def my_expired_token_callback(*kwargs: Any) -> Tuple[dict, int]:
    """Override expired token function

    Returns:
        Tuple[dict, int]: Message to describe the content
    """

    # Return a custom error message
    return {
        "status": "expired",
        "message": "Your access is expired",
    }, 401


# Dry landing page
@app.route("/")
def home():
    """Dry landing page"""

    return """<!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Instruct.io API</title>
    </head>
    <body>
        <h1 style="font-size: 50px; text-align: center;">
            Instruct.io API Server
        </h1>
        <p style="text-align: center;">
            For any issues, please contact Benjamin Herrera via email at
            b10@asu.edu
        </p>
    </body>
    </html>"""


#   endregion


#
#   ROUTE HANDLING
#   region
#

# */authentication/
# region
app.register_blueprint(register, url_prefix="/authentication/")
app.register_blueprint(refresh, url_prefix="/authentication/")
app.register_blueprint(login, url_prefix="/authentication/")
app.register_blueprint(who_am_i, url_prefix="/authentication/")
app.register_blueprint(signout, url_prefix="/authentication/")
# endregion

# */instructions/
# region
app.register_blueprint(create_instruction_group, url_prefix="/instructions/")
app.register_blueprint(get_instruction_group, url_prefix="/instructions/")
app.register_blueprint(
    get_users_instruction_groups, url_prefix="/instructions/"
)
app.register_blueprint(update_instruction_group, url_prefix="/instructions/")
app.register_blueprint(get_checkpoint, url_prefix="/instructions/")
app.register_blueprint(save_checkpoint, url_prefix="/instructions/")
app.register_blueprint(delete_instruction_group, url_prefix="/instructions/")
# endregion

#   endregion


#
#   APP RUNTIME HANDLING
#   region
#

# Main run thread
if __name__ == "__main__":
    # Import waitress
    from waitress import serve

    # Check if the server is in development mode
    mode_type = int(os.environ.get("RUN_MODE"))
    if mode_type == 0:
        print("Running API Server in DEVELOPMENT MODE")
        app.run(host="0.0.0.0", port=5000)
    # Check if the server is in production mode
    elif mode_type == 1:
        print("Running API Server in PRODUCTION MODE")
        serve(app, host="0.0.0.0", port=5000)
    # If the mode value was not provided, exit with a message
    else:
        print("Invalid mode specification. Exiting...")
        exit()


#   endregion
