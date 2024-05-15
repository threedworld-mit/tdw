from tdw.controller import Controller


class TestController(Controller):
    """
    This test controller binds the socket to a random available port.
    """

    def _bind_socket(self, port: int) -> int:
        return self.socket.bind_to_random_port('tcp://*')
