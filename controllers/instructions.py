# Imports
from util.dict_obj import DictObj
from models.instruction_group import InstructionGroup
from ._base import Controller
import uuid

# Extract supabase
supabase = Controller.supabase


class InstructionControl(Controller):
    """Class that demonstrates the control logic of Instruction(s) model(s)"""

    # Extract supabase
    supabase = Controller.supabase

    @staticmethod
    @Controller.return_dict_obj
    def create_instruction_group(name: str) -> DictObj:
        "Create a new instruction group"

        # Prep data to be inserted
        ig_uid = uuid.uuid4().hex
        i_uid = uuid.uuid4().hex

        # Insert a record for the instruction group
        supabase.table("instruction_group").insert(
            {"ig_uid": ig_uid, "group_name": name, "start_point": i_uid}
        ).execute()

        # Create a starting instruction for the instruction group
        supabase.table("instruction").insert(
            {
                "i_uid": i_uid,
                "ig_uid": ig_uid,
                "instruction_title": f"{name} Step #1",
            }
        ).execute()

        # Return a statement
        return Controller.success("Instruction group created")

    @staticmethod
    @Controller.return_dict_obj
    def get_instruction_group_info(ig_uid: str):
        """Get the information of the specified instruction group"""

        # Fetch and return information about the given ig_uid
        try:
            data = (
                supabase.table("instruction_group")
                .select("*")
                .eq("ig_uid", ig_uid)
                .execute()
            )
            return Controller.success(InstructionGroup(**data.data[0]))

        # Return a message if any error occurred
        except Exception:
            return Controller.error("Instruction group not found")

    @staticmethod
    @Controller.return_dict_obj
    def get_instruction_group_instructions(ig_uid: str):
        """Get all the instructions pertaining the the instruction group"""

        # Check if the instruction group exists
        ig = InstructionControl.get_instruction_group_info(ig_uid)
        if ig.status == "error":
            return ig
        ig = ig.message

        # Get all instructions that fall under the instruction group
        data = (
            supabase.table("instruction")
            .select("*")
            .eq("ig_uid", ig_uid)
            .execute()
        )

        # Create a memoization of the queried data
        mapped_sampled = {}
        for i in data.data:
            i = DictObj(i)
            mapped_sampled[i.i_uid] = i

        # Begin sorting the instructions
        result = [mapped_sampled[ig.info.start_point]]
        while (result[-1]["next"] is not None):
            result.append(mapped_sampled[result[-1]["next"]])

        # Return a success message if all is good
        return Controller.success(result)
