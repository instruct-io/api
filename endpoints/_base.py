# Imports
from flask_jwt_extended import jwt_required, decode_token
from inspect import signature, Parameter
from typing import Callable, Any, Tuple
from util.typing import is_valid_type
from functools import wraps
from flask import request
import traceback


def success(message: str, **kwargs: Any) -> dict:
    """Return success message

    Args:
        message (str): Success message

    Returns:
        dict: Message and return code
    """

    # Prep the message
    message = {"status": "success", "message": message}
    message.update(kwargs)

    # Return response
    return message, 200


def client_error(message: str, **kwargs: Any) -> dict:
    """Return a client error message

    Args:
        message (str): Message of error

    Returns:
        dict: Message and return code
    """

    # Prep the message
    message = {"status": "error", "message": message}
    message.update(kwargs)

    # Return response
    return message, 400


def server_error(message: str, **kwargs: Any) -> dict:
    """Return a server error message

    Args:
        message (str): Message of error

    Returns:
        dict: Message and return code
    """
    # Prep the message
    message = {"status": "error", "message": message}
    message.update(kwargs)

    # Return response
    return message, 500


def param_check(func: Callable) -> Callable:
    """
    Decorator to require specified JSON fields in a Flask route

    Args:
        func (Callable): The Flask route function to be wrapped

    Returns:
        Callable: The wrapped function
    """

    @wraps(func)
    def decorated_function(*args: Any, **kwargs: Any) -> Tuple[Any, int]:
        """
        The function that is called in place of the original Flask route
        function. This function adds additional behavior to check the JSON
        body for required fields

        Returns:
            Tuple[Any, int]: The response from the Flask route or an error
            message with a status code
        """

        # Get the request information
        json_data = request.json or {}
        if "_id" in json_data:
            del json_data["_id"]

        # Iterate through the wrapped function's parameters
        sig = signature(func)
        for param in sig.parameters.values():
            # Skip if the current parameter is a kwargs
            if param.name == "_id":
                continue

            # Skip parameters with default values if they are not in json_data
            if (
                param.name not in json_data
                and param.default == Parameter.empty
            ):
                return client_error(f"Missing {param.name} value")

            # Check type only if the parameter is in json_data
            if param.name in json_data and param.annotation != Parameter.empty:
                if not is_valid_type(json_data[param.name], param.annotation):
                    return client_error(
                        f"Invalid type for {param.name}, "
                        + f"expected {param.annotation}"
                    )

        # Execute the wrapped function
        return func(*args, **kwargs, **json_data)

    # Execute the wrapped function
    return decorated_function


def error_handler(func: Callable) -> Callable:
    """Wrap the entire endpoint with a try and except block

    Args:
        func (Callable): Function to wrap with a try and except block

    Returns:
        Callable: Result of the function or an error message
    """

    @wraps(func)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        """Wrapping definition

        Returns:
            Any: Result of the function being wrapped or an error message
        """

        # Try to execute the function
        try:
            return func(*args, **kwargs)

        # If the exception occurs, print the error to the console and
        # return a server error response
        except Exception:
            print(f"Caught an exception in {func.__name__}():")
            traceback.print_exc()
            return server_error("A server error occurred")

    # Return the wrapper
    return decorated_function


def token_required(func: Callable) -> Callable:
    """Decorator to check if endpoint has the proper JWT passed through

    Args:
        func (Callable): Endpoint to wrap

    Returns:
        Callable: Result of the endpoint or an error message
    """

    @wraps(func)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        """Wrapping definition

        Returns:
            Any: Result of the function being wrapped or an error message
        """

        # Extract the access JWT token from the Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header:
            try:
                token_type, token = auth_header.split()
                if token_type.lower() != "bearer":
                    raise ValueError("Invalid token type")
            except ValueError:
                return {"error": "Invalid token format"}, 401
        else:
            return {"error": "Authorization header is missing"}, 401

        # Add token to kwargs and call the original function
        kwargs["_id"] = decode_token(token)["sub"]["_id"]
        return func(*args, **kwargs)

    # Return the wrapper
    return decorated_function
