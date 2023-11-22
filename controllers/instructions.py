# Imports
from util.dict_obj import DictObj
from ._base import Controller
from typing import Any
import uuid

# Extract supabase
supabase = Controller.supabase


class InstructionControl(Controller):
    """Class that demonstrates the control logic of Instruction(s) model(s)"""

    # Extract supabase
    supabase = Controller.supabase

    @staticmethod
    @Controller.return_dict_obj
    def create_instruction_group(**kwargs: Any) -> DictObj:
        "Create a new instruction group"

        # Prep data to be inserted
        data = DictObj(locals()["kwargs"])
        ig_uid = uuid.uuid4().hex
        i_uid = uuid.uuid4().hex

        # Insert a record for the instruction group
        supabase.table("instruction_group").insert(
            {"ig_uid": ig_uid, "group_name": data.name, "start_point": i_uid}
        ).execute()

        # Create a starting instruction for the instruction group
        supabase.table("instruction").insert(
            {
                "i_uid": i_uid,
                "ig_uid": ig_uid,
                "instruction_title": f"{data.name} Step #1",
            }
        ).execute()

        # Return a statement
        return Controller.success("Instruction group created")
