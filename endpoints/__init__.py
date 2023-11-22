# Import
from flask import Blueprint

# */authentication/
# region
register = Blueprint("register", __name__)
login = Blueprint("login", __name__)
who_am_i = Blueprint("who_am_i", __name__)
refresh = Blueprint("refresh", __name__)
# endregion

# */instructions/
# region
create_instruction_group = Blueprint("create_instruction_group", __name__)
get_instruction_group_instructions = Blueprint(
    "get_instruction_group_instructions", __name__
)
# endregion
