from base64 import b64decode
from struct import unpack
from array import array
from typing import List


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
