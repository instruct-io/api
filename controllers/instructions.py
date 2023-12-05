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
        # Since Supabase handles the SQL for us this is the command that
        #   supabase is running in the backend to perform these commands
        #   on a PSQL database
        # INSERT INTO instruction_group (ig_uid, group_name, start_point)
        #   VALUES (ig_uid, name, i_uid);
        supabase.table("instruction_group").insert(
            {"ig_uid": ig_uid, "group_name": name, "start_point": i_uid}
        ).execute()

        # Insert a record for the ownership table
        # INSERT INTO ownership (ownership_uid, account_uid, ig_uid)
        # VALUES (o_uid, supabase.auth.get_user(access_token).user.id,
        #   ig_uid,);
        supabase.table("ownership").insert(
            {
                "ownership_uid": o_uid,
                "account_uid": supabase.auth.get_user(access_token).user.id,
                "ig_uid": ig_uid,
            }
        ).execute()

        # Create a starting instruction for the instruction group
        # INSERT INTO instruction (i_uid, ig_uid, instruction_title)
        # VALUES (i_uid, ig_uid, f"{name} Step #1"));
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
            # SELECT *
            # FROM instruction_group
            # WHERE ig_uid = 'ig_uid';
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
        # SELECT ig_uid
        # FROM ownership
        # WHERE account_uid = 'user_id';
        ig_uids, _ = (
            supabase.table("ownership")
            .select("ig_uid")
            .eq("account_uid", user_id)
            .execute()
        )

        # Iterate through the list and the each IG UID's name
        owner_groups = []
        pprint(ig_uids)
        for i in ig_uids[1]:
            i = DictObj(i)
            # SELECT group_name
            # FROM instruction_group
            # WHERE ig_uid = 'ig_uid';
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
        # SELECT *
        # FROM instruction
        # WHERE ig_uid = 'your_ig_uid_value';
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
    def get_checkpoint(ig_uid: str, access_token: str) -> DictObj:
        """Controller to get the checkpoint data for the user's sessions"""

        # Check if the instruction group exists
        ig = InstructionControl.get_instruction_group_info(ig_uid)
        if ig.status == "error":
            return ig

        # Get user ID
        user_id = supabase.auth.get_user(access_token).user.id

        # Gather the savepoint ID
        # SELECT *
        # FROM save_data
        # WHERE account_uid = user_id
        # AND ig_uid = ig_uid;
        (_, data), _ = (
            supabase.table("save_data")
            .select("*")
            .eq("account_uid", user_id)
            .eq("ig_uid", ig_uid)
            .execute()
        )

        # Return the savepoint content
        return Controller.success(data[0]["i_uid"] if data else "N/A")

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
                # DELETE FROM instruction
                # WHERE i_uid = i;
                supabase.table("instruction").delete().eq("i_uid", i).execute()

        # Iterate through the new instructions and update as such
        for i in new_map:
            # Wrap iterated item in DictObj
            item = DictObj(new_map[i])

            # If the iteration exists in the original, update
            if i in original_map and original_map[i] != new_map[i]:
                # UPDATE instruction
                # SET
                # prev = item.prev,
                # next = item.next,
                # instruction_title = item_instruction_title,
                # description = item.description
                # WHERE i_uid = i;
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
                # INSERT INTO instruction (i_uid, prev, next, ig_uid,
                #   instruction_title, description)
                # VALUES (
                # 'your_i_uid_value',
                # item.prev,
                # item.next,
                # ig_uid,
                # item.instruction_title,
                # item.description
                # );
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
        # UPDATE instruction_group
        # SET
        # start_point = starting_node.i_uid
        # WHERE ig_uid = ig_uid';
        supabase.table("instruction_group").update(
            {
                "start_point": starting_node.i_uid,
            }
        ).eq("ig_uid", ig_uid).execute()

        # endregion

        # Return result
        return Controller.success("Update is a success")

    @staticmethod
    @Controller.return_dict_obj
    def save_checkpoint(i_uid: str, ig_uid: str, access_token: str) -> DictObj:
        """Controller to handle the saving of a user's checkpoint"""

        # Check if the instruction group exists
        ig = InstructionControl.get_instruction_group_info(ig_uid)
        if ig.status == "error":
            return ig

        # Check if the instruction exists
        try:
            # SELECT *
            # FROM instruction
            # WHERE i_uid = i_uid
            # AND ig_uid = ig_uid;
            _ = (
                supabase.table("instruction")
                .select("*")
                .eq("i_uid", i_uid)
                .eq("ig_uid", ig_uid)
                .execute()
            )
        except Exception:
            return Controller.error("Instruction doesn't exist")

        # Get user ID
        user_id = supabase.auth.get_user(access_token).user.id

        # Gather the savepoint ID
        # SELECT *
        # FROM save_data
        # WHERE account_uid = 'your_user_id_value'
        # AND ig_uid = 'your_ig_uid_value';
        (_, data), _ = (
            supabase.table("save_data")
            .select("*")
            .eq("account_uid", user_id)
            .eq("ig_uid", ig_uid)
            .execute()
        )

        # If there's no existing checkpoint, make one
        if not data:
            # Make savepoint IDs
            sp_uid = str(uuid.uuid4().hex)
            sp_uid = (
                f"{sp_uid[:8]}-{sp_uid[8:12]}-{sp_uid[12:16]}-"
                + f"{sp_uid[16:20]}-{sp_uid[20:]}"
            )

            # Insert data
            # INSERT INTO save_data (savepoint_uid, account_uid, ig_uid, i_uid)
            # VALUES (sp_uid, user_id, ig_uid, i_uid);
            supabase.table("save_data").insert(
                {
                    "savepoint_uid": sp_uid,
                    "account_uid": user_id,
                    "ig_uid": ig_uid,
                    "i_uid": i_uid,
                }
            ).execute()

        # If not, update it
        else:
            # UPDATE save_data
            # SET i_uid = 'your_i_uid_value'
            # WHERE account_uid = 'your_user_id_value'
            # AND ig_uid = 'your_ig_uid_value';
            supabase.table("save_data").update(
                {
                    "i_uid": i_uid,
                }
            ).eq(
                "account_uid", user_id
            ).eq("ig_uid", ig_uid).execute()

        # Send updated status
        return Controller.success("Checkpoint saved")

    @staticmethod
    @Controller.return_dict_obj
    def delete_instruction_group(ig_uid: str, access_token: str) -> DictObj:
        """Controller to delete instruction groups"""

        # Check if the instruction group exists
        ig = InstructionControl.get_instruction_group_info(ig_uid)
        if ig.status == "error":
            return ig

        # Get user ID
        user_id = supabase.auth.get_user(access_token).user.id

        # Check if the user is an owner of the instruction group
        try:
            # SELECT *
            # FROM ownership
            # WHERE account_uid = user_id
            # AND ig_uid = ig_uid;
            _ = (
                supabase.table("ownership")
                .select("*")
                .eq("account_uid", user_id)
                .eq("ig_uid", ig_uid)
                .execute()
            )
        except Exception:
            return Controller.error(
                "You don't have ownership of this instruction group"
            )

        # Delete the user's ownership on the ownership relation
        # DELETE FROM ownership
        # WHERE account_uid = 'user_id'
        # AND ig_uid = 'ig_uid';
        supabase.table("ownership").delete().eq("account_uid", user_id).eq(
            "ig_uid", ig_uid
        ).execute()

        # Delete all savepoint data in the save data relation
        # DELETE FROM save_data
        # WHERE ig_uid = 'ig_uid'
        supabase.table("save_data").delete().eq("ig_uid", ig_uid).execute()

        # Delete the the instruction group on the instruction group relation
        # DELETE FROM instruction_group
        # WHERE ig_uid = 'ig_uid'
        supabase.table("instruction_group").delete().eq(
            "ig_uid", ig_uid
        ).execute()

        # Return success message
        return Controller.success("Deletion complete")
