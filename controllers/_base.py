# Imports
from util.dict_obj import DictObj
from config.config import config
from functools import wraps
from typing import Any
import pymongo
import os


class Controller:
    """Encapsulation of all database actions"""

    # Get the different database configurations based on the run type
    if int(os.environ.get("RUN_MODE")) == 1:
        db_spec = config.database.production
    else:
        db_spec = config.database.development

    # Set MongoDB information based on the database specifications
    if db_spec.user != "" and db_spec.password != "":
        CLIENT = pymongo.MongoClient(
            f"mongodb://{db_spec.user}:{db_spec.password}@{db_spec.domain}"
            + f":{db_spec.port}/{db_spec.db}"
        )
        DB = CLIENT[db_spec.db]
    else:
        CLIENT = pymongo.MongoClient(
            f"mongodb://{db_spec.domain}:{db_spec.port}/"
        )
        DB = CLIENT[db_spec.db]

    # Collection constant definition
    USER_COL = DB["users"]
    BLACKLIST_COL = DB["jwtBlacklist"]
    INSTRUCTION_GROUP_COL = DB["instructionGroups"]
    CHECKPOINT_COL = DB["checkpoints"]

    # Set config constants
    DB_SPECS = db_spec
    CONFIG = config

    def error(message: str, **kwargs: Any) -> dict:
        """Returns an error message

        Args:
            message (str): Message to return

        Returns:
            dict: Message in dictionary format
        """

        # Prep the message
        message = {"status": "error", "message": message}
        message.update(kwargs)

        # Return the success message
        return message

    def success(message: str, **kwargs: Any) -> dict:
        """Returns a success message

        Args:
            message (str): Message to return

        Returns:
            dict: Message in dictionary format
        """

        # Prep the message
        message = {"status": "success", "message": message}
        message.update(kwargs)

        # Return the success message
        return message

    def return_dict_obj(func: object) -> object:
        """Wrapper to return controller function's returns in DictObj format

        Args:
            func (object): Function to convert its return format

        Returns:
            object: Return format
        """

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> DictObj:
            """Wrapping definition"""

            # Return with parsing wrapping if all else is good
            return DictObj(func(*args, **kwargs))

        # End of wrapper definition
        return wrapper
