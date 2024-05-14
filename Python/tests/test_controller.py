from typing import List
from tdw.controller import Controller
from tdw.output_data import OutputData


class TestController(Controller):
    """
    This test controller binds the socket to a random available port.
    """

    def _bind_socket(self, port: int) -> int:
        return self.socket.bind_to_random_port('tcp://*')

    def get_output_data(self, resp: List[bytes], r_id: str) -> bytes:
        for i in range(len(resp) - 1):
            if r_id == OutputData.get_data_type_id(resp[i]):
                return resp[i]
        raise Exception(f"Output data {r_id} not found.")
