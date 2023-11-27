from io import BytesIO
from zipfile import ZipFile
from abc import ABC, abstractmethod
from argparse import ArgumentParser
from json import dumps
from typing import List, Optional, final
import asyncio
from websockets.server import serve
from websockets import WebSocketServerProtocol, ConnectionClosedError, ConnectionClosed
import zmq
from tdw.controller import Controller
from tdw.webgl.trial_playback import TrialPlayback


class TrialController(ABC):
    def __init__(self):
        # Get the initial trials.
        self._trials: List[dict] = self.get_initial_trials()
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
    def get_initial_trials(self) -> List[dict]:
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
            # Stop if there are no more trials.
            if len(self._trials) == 0:
                break
            # Send the next trials.
            try:
                await websocket.send(dumps(self._trials))
                self._trials.clear()
            except ConnectionClosed as e:
                print(e)
                break
            # Receive end-of-trial data.
            try:
                bs: bytes = await websocket.recv()
            except ConnectionClosed as e:
                print(e)
                break
            # Parse the playback.
            playback = TrialPlayback()
            with ZipFile(BytesIO(bs), "r") as z:
                playback.read_zip(z=z)
            # Get new trials to send.
            self._trials = self.get_next_trials(playback=playback)
            # Send the logged end-state data.
            if self._log_socket_connected:
                try:
                    self._log_socket.send(bs)
                    self._log_socket.recv()
                except zmq.ZMQError as e:
                    print(e)
                    break

            done = len(self._trials) == 0
        # Close the log socket.
        if self._log_socket_connected:
            self._log_socket_connected = False
            self._log_socket.close()

    @abstractmethod
    def get_next_trials(self, playback: TrialPlayback) -> List[dict]:
        """
        :param playback: The playback of the most recent trial.

        :return: A list of trials to be immediately sent to the WebGL build.
        """

        raise Exception()


def run(controller: TrialController) -> None:
    """
    Run a controller. The controller will continue to try to serve data until its process is killed.

    :param controller: A TrialController.
    """

    # Get the port from command-line arguments.
    parser = ArgumentParser()
    parser.add_argument("port", type=int, help="The WebSocket port.")
    args, unknown = parser.parse_known_args()
    # Set the port.
    controller.set_port(port=args.port)
    # Run the controller.
    asyncio.run(controller.main())
