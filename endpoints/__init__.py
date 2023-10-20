# Import
from flask import Blueprint

# Blueprints for: /example/
# region
create_example = Blueprint("create_example", __name__)
# endregion

# Import views
from . import example  # noqa
