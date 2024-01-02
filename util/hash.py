# Imports
import hashlib


def sha256(string: str, seed: str) -> str:
    """SHA256 hasher function with spicer

    Args:
        string (str): String to hash
        seed (str): Spicer

    Returns:
        str: Hashed string
    """
    return hashlib.sha256((string+seed).encode()).hexdigest()
