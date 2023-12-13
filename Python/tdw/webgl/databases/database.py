import zmq


class Database:
    """
    This is the minimal framework for a Database.
    This will receive data over a socket, do nothing with it, and run indefinitely.
    """

    def __init__(self, port: int):
        """
        :param port: The port that the Database uses.
        """

        context = zmq.Context()
        self._socket: zmq.Socket = context.socket(zmq.REP)
        self._socket.bind(f'tcp://*:{port}')

    def run(self) -> None:
        """
        Run the Database process.
        """

        done = False
        while not done:
            # Receive a message from a TrialController.
            message = self._socket.recv_multipart()
            # Send an empty response.
            self._socket.send(b'')
            # Do something with the message.
            self.on_receive_data(message[0], message[1])
            # Check if we're done.
            done = self.is_done()
        self._socket.close()

    def on_receive_data(self, data: bytes, session_id: bytes) -> None:
        """
        By default, this function does nothing.

        Override this function to do something with data received from a TrialController.

        :param data: The gzip per-trial data received from a TrialController.
        :param session_id: The unique session ID.
        """

        pass

    def is_done(self) -> bool:
        """
        By default, this function always returns False.

        Override this function to add programmatic instructions for stopping the Database process.

        :return: True if the Database should stop.
        """

        return False
