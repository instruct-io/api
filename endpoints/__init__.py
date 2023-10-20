# Import
from flask import Blueprint

# */example/
# region
create_example = Blueprint("create_example", __name__)
# endregion

# */authentication/
# region
register = Blueprint("register", __name__)
login = Blueprint("login", __name__)
who_am_i = Blueprint("who_am_i", __name__)
refresh = Blueprint("refresh", __name__)
# endregion


# Import views
from . import example_  # noqa
