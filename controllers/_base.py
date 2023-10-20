# Imports
from supabase import create_client
from util.dict_obj import DictObj
from config.config import config
from functools import wraps
from typing import Any
import os


class Controller:
    """Encapsulation of all database actions"""

    # Get the different database configurations based on the run type
    db_spec = None
    if int(os.environ.get("RUN_MODE")) == 1:
        db_spec = config.database.production
    else:
        db_spec = config.database.development

    # Set create supabase connection based on the database specifications
    if db_spec.url != "<< TBD >>" or db_spec.key != "<< TBD >>":
        supabase = create_client(db_spec.url, db_spec.key)

    # Set config constants
    DB_SPECS = db_spec
    CONFIG = config

    def sendError(message: str, **kwargs: Any) -> dict:
        """Error message format method"""

        # Prep the message
        message = {"status": "error", "message": message}
        message.update(kwargs)

        # Return the success message
        return message

    def sendSuccess(message: str, **kwargs: Any) -> dict:
        """Success message format method"""

        # Prep the message
        message = {"status": "success", "message": message}
        message.update(kwargs)

        # Return the success message
        return message

    def return_dict_obj(func: object) -> object:
        """Dictionary to custom dictionary object wrapper"""

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> DictObj:
            """Wrapping definition"""

            # Return with parsing wrapping if all else is good
            return DictObj(func(*args, **kwargs))

        # End of wrapper definition
        return wrapper
