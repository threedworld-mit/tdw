from io import BytesIO
from zipfile import ZipFile
from abc import ABC, abstractmethod
from argparse import ArgumentParser
from json import dumps
from typing import List, Optional, final
import asyncio
from websockets.server import serve
from websockets import WebSocketServerProtocol, ConnectionClosed
import zmq
from tdw.webgl.trial_playback import TrialPlayback
from tdw.webgl.trial_adders.end_simulation import EndSimulation
from tdw.webgl.trial_message import TrialMessage
from tdw.webgl.trial_message_encoder import TrialMessageEncoder


class TrialController(ABC):
    def __init__(self):
        """
        (no arguments)
        """

        # Get the initial trial message.
        self._trial_message: TrialMessage = self.get_initial_message()
        self._port: int = -1
        self._log_socket: Optional[zmq.Socket] = None
        self._log_socket_connected: bool = False

    @final
    def set_port(self, port: int) -> None:
        """
        Set the port of the connection with the client WebGL build.
        This is called with `launch()` and must be called before calling `main()`.

        :param port: The WebSocket port.
        """

        self._port = port

    @final
    def connect_log_socket(self, address: str) -> None:
        """
        Connect the socket used to send end-trial log data.

        :param address: The `address:port` of the listening socket.
        """

        context = zmq.Context()
        self._log_socket = context.socket(zmq.REQ)
        self._log_socket.connect(f'tcp://{address}')
        self._log_socket_connected = True

    @abstractmethod
    def get_initial_message(self) -> TrialMessage:
        """
        :return: An initial `TrialMessage` that will be sent to the build.
        """

        raise Exception()

    @abstractmethod
    def get_next_message(self, playback: TrialPlayback) -> TrialMessage:
        """
        :param playback: The playback of the most recent trial.

        :return: The next `TrialMessage` to be sent to the build.
        """

        raise Exception()

    @final
    async def main(self) -> None:
        """
        Run the TrialController until it stops sending trials or the connection is lost.
        """

        await serve(self._run, "", self._port, extra_headers={"Access-Control-Allow-Origin": "true"})

    @final
    async def _run(self, websocket: WebSocketServerProtocol) -> None:
        """
        Run the TrialController until there are no more trials to be sent.

        :param websocket: The websocket.
        """

        done = False
        while not done:
            # Send the next trials.
            try:
                await websocket.send(dumps(self._trial_message, cls=TrialMessageEncoder))
            except ConnectionClosed as e:
                print(e)
                done = True
                continue
            # We're done now.
            if isinstance(self._trial_message.adder, EndSimulation):
                done = True
                continue
            # Receive end-of-trial data.
            try:
                bs: bytes = await websocket.recv()
            except ConnectionClosed as e:
                print(e)
                done = True
                continue
            # Parse the playback.
            playback = TrialPlayback()
            with ZipFile(BytesIO(bs), "r") as z:
                playback.read_zip(z=z)
            # Send the logged end-state data.
            if self._log_socket_connected:
                try:
                    self._log_socket.send(bs)
                    self._log_socket.recv()
                    # Get the next trial message, which will be sent at the top of the loop.
                    self._trial_message = self.get_next_message(playback=playback)
                except zmq.ZMQError as e:
                    print(e)
                    # Send a kill signal.
                    self._trial_message = TrialMessage(trials=[], adder=EndSimulation())
        # Close the log socket.
        if self._log_socket_connected:
            self._log_socket_connected = False
            self._log_socket.close()


def run(controller: TrialController) -> None:
    """
    Run a controller. The controller will continue to try to serve data until its process is killed.

    :param controller: A TrialController.
    """

    # Get the port from command-line arguments.
    parser = ArgumentParser()
    parser.add_argument("port", type=int, help="The WebSocket port")
    parser.add_argument("database_address", type=str, default="", help="The database address:port")
    args, unknown = parser.parse_known_args()
    # Set the port.
    controller.set_port(port=args.port)
    # Connect to the database.
    if args.database_address != "":
        controller.connect_log_socket(address=args.database_address)
    # Run the controller.
    asyncio.run(controller.main())
