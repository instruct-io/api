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
get_instructions = Blueprint("get_instructions", __name__)
get_instruction_groups = Blueprint("get_instruction_groups", __name__)
update_instructions = Blueprint("update_instructions", __name__)
get_checkpoint = Blueprint("get_checkpoint", __name__)
save_checkpoint = Blueprint("save_checkpoint", __name__)
delete_instruction_group = Blueprint("delete_instruction_group", __name__)
# endregion
