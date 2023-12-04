# Imports
from config.config import config
from util.dict_obj import DictObj
from models.instruction_group import InstructionGroup
from ._base import Controller
from typing import List
from pprint import pprint  # noqa
import uuid
import re


# Extract supabase
supabase = Controller.supabase


class InstructionControl(Controller):
    """Class that demonstrates the control logic of Instruction(s) model(s)"""

    # Extract supabase
    supabase = Controller.supabase

    @staticmethod
    @Controller.return_dict_obj
    def create_instruction_group(name: str, access_token: str) -> DictObj:
        "Create a new instruction group"

        # Prep data to be inserted+
        ig_uid = str(uuid.uuid4().hex)
        i_uid = str(uuid.uuid4().hex)
        i_uid = (
            f"{i_uid[:8]}-{i_uid[8:12]}-{i_uid[12:16]}-"
            + f"{i_uid[16:20]}-{i_uid[20:]}"
        )
        o_uid = str(uuid.uuid4().hex)
        o_uid = (
            f"{o_uid[:8]}-{o_uid[8:12]}-{o_uid[12:16]}-"
            + f"{o_uid[16:20]}-{o_uid[20:]}"
        )

        # Insert a record for the instruction group
        supabase.table("instruction_group").insert(
            {"ig_uid": ig_uid, "group_name": name, "start_point": i_uid}
        ).execute()

        # Insert a record for the ownership table
        supabase.table("ownership").insert(
            {
                "ownership_uid": o_uid,
                "account_uid": supabase.auth.get_user(access_token).user.id,
                "ig_uid": ig_uid,
            }
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
    def get_instruction_group_info(ig_uid: str) -> DictObj:
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
    def get_instruction_groups(access_token: str) -> DictObj:
        """Controller to get the user's instruction groups"""

        # Get user ID
        user_id = supabase.auth.get_user(access_token).user.id
        # Get a list of IG_UIDs
        ig_uids, _ = (
            supabase.table("ownership")
            .select("ig_uid")
            .eq("account_uid", user_id)
            .execute()
        )

        # Iterate through the list and the each IG UID's name
        owner_groups = []
        for i in ig_uids[1]:
            i = DictObj(i)
            res, _ = (
                supabase.table("instruction_group")
                .select("group_name")
                .eq("ig_uid", i.ig_uid)
                .execute()
            )
            owner_groups.append(
                {"ig_uid": i.ig_uid, "group_name": res[1][0]["group_name"]}
            )

        # Return list of owned instruction groups
        return Controller.success(owner_groups)

    @staticmethod
    @Controller.return_dict_obj
    def get_instructions(ig_uid: str) -> DictObj:
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
        while result[-1]["next"] is not None:
            result.append(mapped_sampled[result[-1]["next"]])

        # Return a success message if all is good
        return Controller.success(result)

    @staticmethod
    @Controller.return_dict_obj
    def update_instructions(
        ig_uid: str, new_instructions: List[dict]
    ) -> DictObj:
        """Controller to update the instructions for an instruction group"""

        #
        #   DATA CHECK
        #

        # region

        # Check (1) if there's a forward loop,
        # (2) no mismatch IG UID,
        # (3) no repeating instruction UIDs,
        # (4) and no improper instruction UIDs
        # ALSO: Create a mapper for it; and get the starting and ending nodes
        forward_tracker = set()
        starting_node = None
        ending_node = None
        new_map = {}
        for i in new_instructions:
            # Check for loops
            if i["next"] in forward_tracker:
                return Controller.error("New list forms a loop", node=i)

            # Check for out-of-group instructions
            if i["ig_uid"] != ig_uid:
                return Controller.error(
                    "One item is not part of the instruction group", node=i
                )

            # Check for repeating instructions
            if i["i_uid"] in new_map:
                return Controller.error("One item is a repeat")

            # Check for instruction IDs that are in the correct format
            if not bool(re.match(config.id_regex, i["i_uid"])):
                return Controller.error(
                    "Item ID is not in correct ID format", node=i
                )

            # Check if there is only one starting and ending node
            if starting_node and not i["prev"]:
                return Controller.error(
                    "There can only be one starting node", node=i
                )
            if ending_node and not i["next"]:
                return Controller.error(
                    "There can only be one ending node", node=i
                )

            # Add to trackers and mapper
            forward_tracker.add(i["i_uid"])
            new_map[i["i_uid"]] = i

            # Add starting node if there's no previous pointer
            if not starting_node and not i["prev"]:
                starting_node = DictObj(i)
            if not ending_node and not i["next"]:
                ending_node = DictObj(i)

        # Check if there's a backward loop and that all prev and next pointers
        # point to set of instructions iin the IG
        backward_tracker = set()
        for i in new_instructions[::-1]:
            # Check if there's a backward loop
            if i["prev"] in backward_tracker or i["prev"] == i["i_uid"]:
                return Controller.error("New list forms a loop", node=i)

            # Check if there's a pointer that doesn't point to the IG
            if i["prev"] and i["prev"] not in new_map:
                return Controller.error(
                    "Item has incorrect previous pointer", node=i
                )
            if i["next"] and i["next"] not in new_map:
                return Controller.error(
                    "Item has incorrect next pointer", node=i
                )

            backward_tracker.add(i["i_uid"])

        # Set the next of the last node and the prev of the first to NULL
        new_instructions[-1]["next"] = None
        new_instructions[0]["prev"] = None

        # endregion

        #
        #   PREPARATION
        #

        # region

        # Get the original steps
        original = InstructionControl.get_instructions(ig_uid)

        # If the given UID doesn't exist, return error
        # Else, extract the message
        if original.status == "error":
            return original
        original = original.message

        # Create key mappings for the original
        original_map = {}
        for i in original:
            original_map[i.i_uid] = i

        # endregion

        #
        #   OPERATION
        #

        # region

        # Iterate through the original and delete records
        for i in original_map:
            if i not in new_map:
                supabase.table("instruction").delete().eq("i_uid", i).execute()

        # Iterate through the new instructions and update as such
        for i in new_map:
            # Wrap iterated item in DictObj
            item = DictObj(new_map[i])

            # If the iteration exists in the original, update
            if i in original_map and original_map[i] != new_map[i]:
                supabase.table("instruction").update(
                    {
                        "prev": item.prev,
                        "next": item.next,
                        "instruction_title": item.instruction_title,
                        "description": item.description,
                    }
                ).eq("i_uid", i).execute()

            # If the iteration doesn't exist in the original, add
            elif i not in original_map:
                # Reformulate instruction ID if not in proper structure
                i_uid = item.i_uid
                if not bool(re.match(config.id_regex, i_uid)):
                    i_uid = str(uuid.uuid4().hex)
                    i_uid = (
                        f"{i_uid[:8]}-{i_uid[8:12]}-{i_uid[12:16]}-"
                        + f"{i_uid[16:20]}-{i_uid[20:]}"
                    )

                # Insert into instruction table
                supabase.table("instruction").insert(
                    {
                        "i_uid": i_uid,
                        "prev": item.prev,
                        "next": item.next,
                        "ig_uid": ig_uid,
                        "instruction_title": item.instruction_title,
                        "description": item.description,
                    }
                ).execute()

        # Update the starting node pointer for the instruction group
        supabase.table("instruction_group").update(
            {
                "start_point": starting_node.i_uid,
            }
        ).eq("ig_uid", ig_uid).execute()

        # endregion

        # Return result
        return Controller.success("Update is a success")
