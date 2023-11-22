# Flask Imports
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask import Flask

# Endpoint imports
# region
from endpoints.authentication import register, login
from endpoints.instructions import (
    create_instruction_group,
    get_instruction_group_instructions,
)

# endregion

# Miscellaneous Imports
from config.config import config
from datetime import timedelta
import os


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
    """Function to test if the user's token is blacklisted"""

    # TODO: Create relation to store blacklisted tokens
    """
    # Get the JWT token information
    jti = jwt_payload["jti"]

    # Check if the token is blacklisted
    query = DataAccessBase.BLACKLIST_COL.find_one({"access_jti": jti})

    # Return true if it is, false if not
    return query is not None
    """

    # * TEMP: Return false until TODO is accomplished
    return False


# Customize expired token message
@jwt.expired_token_loader
def my_expired_token_callback(*kwargs):
    """Function to customize the expired token message"""

    # Return a custom error message
    return {
        "status": "expired",
        "message": "Your access is expired",
    }, 401


#   endregion


#
#   ROUTE HANDLING
#   region
#

# */authentication/
# region
app.register_blueprint(register, url_prefix="/authentication/")
app.register_blueprint(login, url_prefix="/authentication/")
# endregion

# */instructions/
# region
app.register_blueprint(create_instruction_group, url_prefix="/instructions/")
app.register_blueprint(
    get_instruction_group_instructions, url_prefix="/instructions/"
)
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
