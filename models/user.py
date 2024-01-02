# Imports
from util.dict_obj import DictObj
from typing import List


class User:
    """User class model"""

    def __init__(
        self: "User",
        _id: str,
        first_name: str,
        last_name: str,
        email: str,
        password: str
    ) -> None:
        """Constructor for the User class

        Args:
            self (User): Current class type
            _id (str): ID of the user
            first_name (str): First name of the user
            last_name (str): Last name of the user
            email (str): Email of the user
            password (str): Password of the user
        """

        # Save info
        self.info = DictObj({k: v for k, v in locals().items() if k != "self"})
        self.info.update(self.info.pop("kwargs", {}))

        # Calculate user's full name
        self.info.full_name = self.get_fullname(lastNameFirst=True)

    def get_generic_info(
        self: "User",
        includeFullName: bool = True,
        lastNameFirst: bool = True,
        other_protections: List[str] = [],
    ) -> DictObj:
        """Returns content that doesn't include any security concerns

        Args:
            self (User): Current class type
            includeFullName (bool, optional): Should the method return the
                user's full name? Defaults to True.
            lastNameFirst (bool, optional): Should the method return the user's
                last name? Defaults to True.
            other_protections (List[str], optional): What other attributes
                should the method not show? Defaults to [].

        Returns:
            DictObj: Returns the content of the user
        """

        # FIlter out any secure data
        data = {
            k: v
            for k, v in self.info.items()
            if k not in ["password"] + other_protections
        }

        # Append full name information to the data based on the
        # given parameters
        if includeFullName:
            data["full_name"] = self.get_fullname(lastNameFirst=lastNameFirst)

        # Return the data
        return data

    def get_fullname(self: "User", lastNameFirst: bool = True) -> str:
        """Returns the user's full name

        Args:
            self (User): Current class type
            lastNameFirst (bool, optional): Should the the full name be last
                name first? Defaults to True.

        Returns:
            str: Full name of the user
        """

        # Get the user's names
        first_name = self.info.first_name
        last_name = self.info.last_name
        middle_initial = ""
        if "middle_initial" in self.info:
            middle_initial = " " + self.info.middle_initial

        # Get the name in different styles based on given options
        if lastNameFirst:
            name = f"{last_name}, {first_name}{middle_initial}"
        else:
            name = f"{first_name}{middle_initial} {last_name}"

        # Return name
        return name
