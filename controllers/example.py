# Imports
from util.dict_obj import DictObj
from ._base import Controller
from models.example import Example
from typing import Any
import uuid


class ExampleControl(Controller):
    """Class that demonstrates the control logic of an Example model"""

    @staticmethod
    @Controller.return_dict_obj
    def create_example(**kwargs: Any) -> DictObj:
        "Insert an Example record into the database"

        # Prep data to be inserted
        data = DictObj(locals()["kwargs"])
        data.id = uuid.uuid4().hex

        # Insert freshly created record into database
        # TODO: Insert data into entity

        # * EXAMPLE: Creating a Model Class
        example_obj = Example(attr1="a", attr2="b", attr3="c", attr4="d")

        # Return a statement
        return Controller.sendSuccess(
            "Example created",
            id=data.id,
            kwargs=kwargs,
            obj_result=example_obj.info,
        )
