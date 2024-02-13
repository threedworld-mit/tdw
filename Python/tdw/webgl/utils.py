from datetime import datetime
from base64 import b64decode
from struct import unpack
from array import array
from typing import List
import numpy as np

# This is the epoch time used by C# timestamps.
EPOCH: np.datetime64 = np.datetime64("00001-01-01T00:00")


def get_output_data(output_data: str) -> List[bytes]:
    """
    :param output_data: Base64-encoded output data.

    :return: Output data as a list of output data byte arrays.
    """

    buffer = b64decode(output_data)
    index = 4
    num_elements = unpack(f"<i", buffer[: index])[0]
    num_elements_offset = num_elements * 4
    a = array("i")
    a.frombytes(buffer[index: index + num_elements_offset])
    element_sizes: List[int] = a.tolist()
    resp: List[bytes] = list()
    index += num_elements_offset
    for element_size in element_sizes:
        resp.append(buffer[index: index + element_size])
        index += element_size
    return resp


def bytes_to_time_delta(ticks: bytes, byte_order: str = "<") -> np.timedelta64:
    """
    :param ticks: 8 bytes that can be unpacked into a 64-bit signed integer.
    :param byte_order: The byte order of `ticks`.

    :return: A numpy.timedelta64 of the ticks. See: https://numpy.org/doc/stable/reference/arrays.datetime.html
    """

    return ticks_to_time_delta(unpack(f"{byte_order}q", ticks)[0])


def ticks_to_time_delta(ticks: int) -> np.timedelta64:
    """
    :param ticks: A 64-bit signed integer of the number of ticks. 1 tick = 10 microseconds.

    :return: A numpy.timedelta64 of the ticks. See: https://numpy.org/doc/stable/reference/arrays.datetime.html
    """

    return EPOCH + np.timedelta64(ticks // 10, "us")


def timedelta64_to_datetime(time_delta: np.timedelta64) -> datetime:
    """
    :param time_delta: A numpy time delta.

    :return: A Python datetime.
    """

    return time_delta.astype(datetime)


def ticks_to_datetime(ticks: int) -> datetime:
    """
    :param ticks: A 64-bit signed integer of the number of ticks. 1 tick = 10 microseconds.

    :return: A Python datetime.
    """

    return timedelta64_to_datetime(EPOCH + np.timedelta64(ticks // 10, "us"))


def bytes_to_datetime(ticks: bytes, byte_order: str = "<") -> datetime:
    """
    :param ticks: 8 bytes that can be unpacked into a 64-bit signed integer.
    :param byte_order: The byte order of `ticks`.

    :return: A Python datetime.
    """

    return ticks_to_datetime(unpack(f"{byte_order}q", ticks)[0])


def string_to_datetime(string: str) -> datetime:
    """
    :param string: A datetime string in the format '%m/%d/%Y %H:%M:%S'.

    :return: A Python datetime.
    """

    return datetime.strptime(string, '%m/%d/%Y %H:%M:%S')
