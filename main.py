# Flask Imports
# ? UNNEEDED :: from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask import Flask

# Endpoint imports
# region
from endpoints.authentication import register, refresh, login, who_am_i
from endpoints.instructions import (
    create_instruction_group,
    get_instructions,
    get_instruction_groups,
    update_instructions,
    get_checkpoint,
    save_checkpoint,
)

# endregion
import os


#
#   FLASK APP CONFIGURATION
#   region
#

# Make app instance
app = Flask(__name__)

# Set CORS for the application
CORS(app, methods=["POST", "GET"])


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
# endregion

# */instructions/
# region
app.register_blueprint(create_instruction_group, url_prefix="/instructions/")
app.register_blueprint(get_instructions, url_prefix="/instructions/")
app.register_blueprint(get_instruction_groups, url_prefix="/instructions/")
app.register_blueprint(update_instructions, url_prefix="/instructions/")
app.register_blueprint(get_checkpoint, url_prefix="/instructions/")
app.register_blueprint(save_checkpoint, url_prefix="/instructions/")
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
