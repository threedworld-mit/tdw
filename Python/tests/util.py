from typing import List
import numpy as np
import pytest
from tdw.output_data import OutputData, QuitSignal
from test_controller import TestController


@pytest.fixture()
def controller(request):
    c = TestController()

    def teardown():
        resp = c.communicate({"$type": "terminate"})
        assert QuitSignal(get_output_data(resp, "quit")).get_ok()
    request.addfinalizer(teardown)

    return c


def get_output_data(resp: List[bytes], r_id: str) -> bytes:
    """
    :param resp: The response from the build.
    :param r_id: The ID of the desired output data.

    :return: The raw byte array of the output data.
    """

    for i in range(len(resp) - 1):
        if r_id == OutputData.get_data_type_id(resp[i]):
            return resp[i]
    raise Exception(f"Output data {r_id} not found.")


def assert_float(a: float, b: float, delta: float = 0.0001) -> None:
    """
    :param a: A float.
    :param b: Another float.
    :param delta: If the difference between a and b is less than this, they are equal.
    """

    c = abs(abs(a) - abs(b))
    if c > delta:
        print(f"{a}, {b}, {c}")
    assert c <= delta


def assert_arr(a: np.ndarray, b: np.ndarray, delta: float = 0.0001) -> None:
    """
    :param a: An array.
    :param b: Another array.
    :param delta: If the difference between a and b is less than this, they are equal.
    """

    assert a.shape == b.shape
    c = np.linalg.norm(a - b)
    if c > delta:
        print(f"{a}, {b}, {c}")
    assert c <= delta
