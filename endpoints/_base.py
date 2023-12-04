# Imports
from config.config import arguments
from typing import List, Any
from functools import wraps
from flask import request
from gotrue.errors import AuthApiError
import traceback


# Export an arguments config variable
ARGS = arguments.endpoints


def success(message: str, **kwargs: Any) -> dict:
    """Returns a message with a success status"""

    # Prep the message
    message = {"status": "success", "message": message}
    message.update(kwargs)

    # Return response
    return message, 200


def client_error(message: str, **kwargs: Any) -> dict:
    """Returns a message with a client error status"""

    # Prep the message
    message = {"status": "error", "message": message}
    message.update(kwargs)

    # Return response
    return message, 400


def server_error(message: str, **kwargs: Any) -> dict:
    """Returns a message with a server error status"""
    # Prep the message
    message = {"status": "error", "message": message}
    message.update(kwargs)

    # Return response
    return message, 500


def arg_check(required_params: List[str]) -> object:
    """Method that checks for minimum parameters"""

    def decorator(func: object) -> object:
        """Decorator definition"""

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """Wrapping definition"""

            # Get the JSON body
            data = request.get_json()

            # Return error if the body was empty
            if data is None:
                return client_error("JSON body is empty")

            # Check if the given arguments has the minimum arguments
            for arg in required_params:
                if arg not in data.keys():
                    return client_error(
                        "Call needs the following arguments: "
                        + ", ".join(required_params)
                    )

            # Return normally if all else is good
            return func(*args, **kwargs)

        # End of wrapper definition
        return wrapper

    # End of decorator definition
    return decorator


def error_handler(func: object) -> object:
    """Decorator to handle errors inside function endpoints"""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """Wrapping definition"""

        # Try to execute the function
        try:
            return func(*args, **kwargs)

        # If the error is an invalid access token, send that message
        except AuthApiError as e:
            return server_error(str(e))

        # If the exception occurs, print the error to the console and
        # return a server error response
        except Exception:
            print(f"Caught an exception in {func.__name__}():")
            traceback.print_exc()
            return server_error("A server error occurred")

    # Return the wrapper
    return wrapper


def token_required(func: object) -> object:
    """Decorator for require token"""

    @wraps(func)
    def decorated_function(*args, **kwargs):
        """Wrapping definition"""

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
        kwargs["access_token"] = token
        return func(*args, **kwargs)

    # Return the wrapper
    return decorated_function
