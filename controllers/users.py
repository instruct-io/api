# Imports
from flask_jwt_extended import decode_token
from typing import List, Any, Union
from util.dict_obj import DictObj
from ._base import Controller
from models.user import User
from util.hash import sha256
from pprint import pprint  # noqa
import datetime
import uuid
import math


class UserControl(Controller):
    """Class that defines the control logic of User information and models

    Args:
        Controller (Controller): Inherits the Controller parent class
    """

    @staticmethod
    @Controller.return_dict_obj
    def register_user(
        first_name: str,
        last_name: str,
        email: str,
        password: str
    ) -> DictObj:
        """Method that handles registering a user to the system

        Args:
            first_name (str): First name of the new user
            last_name (str): Last name of the new user
            email (str): Email of the new user
            phone_number (str): Phone number of the new user
            password (str): Password of the new user

        Returns:
            DictObj: User object
        """

        # Add user to the list and return success if the given
        # information is not the system
        query = {"email": email}
        if Controller.USER_COL.find_one(query) is None:
            # Prep data to be inserted
            data = locals()
            data["_id"] = uuid.uuid4().hex
            data["email"] = data["email"].lower()
            del data["query"]

            # Hash and save the given password
            password = sha256(password, Controller.DB_SPECS.spicer)
            data["password"] = password

            # Insert user into the database and return success
            Controller.USER_COL.insert_one(data)
            return Controller.success("Registration successful!")

        # Return false if the given information exists
        else:
            return Controller.error(
                "You have registered or is already authorized"
            )

    @staticmethod
    @Controller.return_dict_obj
    def login(email: str, password: str) -> Union[User, DictObj]:
        """Method that returns the user object based on the given user and pass

        Args:
            email (str): Email of the user trying to login
            password (str): Password attempt

        Returns:
            Union[User, DictObj]: Returns the user object if successful or an
                error message if not
        """

        # Hash and save the given password to kwargs
        password = sha256(password, Controller.DB_SPECS.spicer)

        # Get the user's information based on the given credentials
        query = {"email": email, "password": password}
        user = Controller.USER_COL.find_one(query)

        # Return with an error if no id was found
        if user is None:
            return Controller.error("Incorrect email or password")

        # Get the user's id
        id = user["_id"]

        # Return user content
        return UserControl.get_user(id)

    @staticmethod
    @Controller.return_dict_obj
    def get_user(id: str, **kwargs: Any) -> DictObj:
        """Base method for get_user methods

        Args:
            id (str): ID of the user to search

        Returns:
            DictObj: A response that contains the user's info in dictionary
                format
        """

        # Get the results from the query
        if id == "_email" and "email" in kwargs:
            user = Controller.USER_COL.find_one({"email": kwargs["email"]})
        else:
            user = Controller.USER_COL.find_one({"_id": id})

        # If no user was found, send an error
        if user is None:
            return Controller.error("User not found")

        # Return results based on types of representation
        return Controller.success(User(**user))

    @staticmethod
    @Controller.return_dict_obj
    def get_users(ids: List[str], **kwargs: Any) -> DictObj:
        """Get a list of users that the given IDs are pertaining to

        Args:
            ids (List[str]): List of users to find

        Returns:
            DictObj: Return a list of user object based on the list of users
        """

        # Get all users that are in the user collection and the ID list
        res = Controller.USER_COL.find({"_id": {"$in": ids}})
        users = list(res)

        # Return result
        return Controller.success([User(**i) for i in users])

    @staticmethod
    @Controller.return_dict_obj
    def get_all_users(page_size: int, page_index: int) -> DictObj:
        """Get a list of users based on the page size and the index

        Args:
            page_size (int): Page size of result
            page_index (int): Index of the page

        Returns:
            DictObj: Result of the search
        """

        # Check if the page_size or page_index is negative
        if page_size <= 0 or page_index < 0:
            return Controller.error("Invalid pagination size or index")

        # Get the total amount of pages based on pagination size
        pages = math.ceil(
            Controller.USER_COL.count_documents()
            / page_size
        )

        # Check if the page_index is outside the page range
        if page_index >= pages:
            return Controller.error("Pagination index out of bounds")

        # Calculate skip value
        skips = page_size * (page_index)

        # Get the list of users based on the given page size and index
        results = (
            Controller.USER_COL.find()
            .skip(skips)
            .limit(page_size)
        )

        # Turn each document into a Unit object
        results = [User(**item) for item in list(results)]

        # Return the results and the page size
        return Controller.success(results, pages=pages)

    @staticmethod
    @Controller.return_dict_obj
    def get_user_with_reset_token(token: str) -> DictObj:
        """Method to get the user object that has an equal reset token

        Args:
            token (str): Token of the password reset

        Returns:
            DictObj: Returns the user's content
        """

        # Find user by token and ensure the token hasn't expired
        user = Controller.USER_COL.find_one(
            {
                "reset_token": token,
                "token_expiry": {"$gte": datetime.datetime.now()},
            }
        )

        # Return the result
        return DictObj(user)

    @staticmethod
    @Controller.return_dict_obj
    def update_user(id: str, **kwargs: Any) -> DictObj:
        """Update the specified user's information

        Args:
            id (str): ID of the user to update

        Returns:
            DictObj: Result of the update
        """

        # Delete the id in the kwargs
        if "_id" in kwargs:
            del kwargs["_id"]
        if "id" in kwargs:
            del kwargs["id"]

        # Check if the unit based on its id does exist
        user = Controller.USER_COL.find_one({"_id": id})
        if user is None:
            return Controller.error("User does not exist")
        user = User(**user)

        # Update full_name if any of the names is different
        if "first_name" in kwargs:
            user.info.first_name = kwargs["first_name"]
        if "middle_initial" in kwargs:
            user.info.middle_initial = kwargs["middle_initial"]
        if "last_name" in kwargs:
            user.info.last_name = kwargs["last_name"]
        kwargs["full_name"] = user.get_fullname()

        # Update the document and return a success message
        Controller.USER_COL.update_one({"_id": id}, {"$set": kwargs})
        return Controller.success("User updated")

    @staticmethod
    @Controller.return_dict_obj
    def update_user_password(id: str, password: str) -> DictObj:
        """Method to update a user's password from password reset request

        Args:
            id (str): Get the ID of the user
            password (str): Get the password to reset

        Returns:
            DictObj: Return the result of the password reset
        """

        # Hash password
        password = sha256(password, Controller.DB_SPECS.spicer)

        # Update the user
        Controller.USER_COL.update_one(
            {"_id": id},
            {
                "$set": {"password": password},
                "$unset": {"reset_token": 1, "token_expiry": 1},
            },
        )

        # Return message
        return Controller.success("Password updated")

    @staticmethod
    @Controller.return_dict_obj
    def handle_jwt_blacklisting(refresh: str, access: str) -> DictObj:
        """Handles the blacklisting of JWT tokens

        Args:
            refresh (str): Refresh JWT information to trash
            access (str): Access JWT information to trash

        Returns:
            DictObj: Result of the blacklist
        """

        # Get the JTI from the tokens
        refresh_jti = decode_token(refresh)["jti"]
        access_jti = decode_token(access)["jti"]

        # Place tokens to blacklist collection
        Controller.BLACKLIST_COL.insert_one(
            {
                "refresh": refresh,
                "access": access,
                "refresh_jti": refresh_jti,
                "access_jti": access_jti,
            }
        )

        # Return message
        return Controller.success("Signed out")
