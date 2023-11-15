from enum import Enum


class LogType(Enum):
    """
    How data should be logged (if at all).
    """

    none = 0  # No logging.
    disk = 1  # Log commands and output data to disk.
    remote = 2  # Send commands and output data over a socket.
