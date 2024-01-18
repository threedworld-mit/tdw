from abc import ABC, abstractmethod
from argparse import ArgumentParser
from json import dumps
from typing import List, Union, Optional, final
from struct import unpack
from array import array
import asyncio
from websockets.server import serve
from websockets import WebSocketServerProtocol, ConnectionClosed
import zmq
from tdw.backend.encoder import Encoder
from tdw.commands.command import Command
from tdw.webgl.trial_playback import TrialPlayback
from tdw.webgl.trial_adders.end_simulation import EndSimulation
from tdw.webgl.trial_message import TrialMessage


END_MESSAGE: TrialMessage = TrialMessage(trials=[], adder=EndSimulation())


class TrialController(ABC):
    """
    Abstract base class for sending TrialMessages to a WebGL build.

    For a minimal example, see: `tdw/Python/tdw/webgl/examples/hello_world.py`
    """

    def __init__(self):
        """
        (no arguments)
        """

        # Get the initial trial message.
        self._trial_message: TrialMessage = self.get_initial_message()
        # The WebSocket port. This is set in `self.set_port(port)`.
        self._port: int = -1
        # The TDW session ID. This is set in `self.set_session_id(session_id)`.
        self._session_id: int = -1
        # This gets sent to the Database.
        self._session_id_bytes: bytes = self._session_id.to_bytes(byteorder="little", signed=True)
        # This is used to connect to a remote Database.
        self._database_socket: Optional[zmq.Socket] = None
        self._database_socket_connected: bool = False
        self._send_trial_message: bool = True
        self._commands: List[Union[Command, dict]] = list()
        # This is used to stop the server.
        self._stop = asyncio.Future()

    @final
    def set_port(self, port: int) -> None:
        """
        Set the port of the connection with the client WebGL build.
        This is called with `launch()` and must be called before calling `main()`.

        :param port: The WebSocket port.
        """

        self._port = port

    @final
    def set_session_id(self, session_id: int) -> None:
        """
        Set the session ID. This is used when sending data to the Database.

        :param session_id: The Session ID.
        """

        self._session_id = session_id

    @final
    def connect_database_socket(self, address: str) -> None:
        """
        Connect the socket used to send end-trial log data.

        :param address: The `address:port` of the listening socket.
        """

        context = zmq.Context()
        self._database_socket = context.socket(zmq.REQ)
        self._database_socket.connect(f'tcp://{address}')
        self._database_socket_connected = True

    @abstractmethod
    def get_initial_message(self) -> TrialMessage:
        """
        :return: An initial `TrialMessage` that will be sent to the build.
        """

        raise Exception()

    def on_receive_trial_end(self, bs: bytes) -> None:
        """
        This is called when the TrialController's WebSocket receives a message at the end of a trial.
        By default, this function doesn't do anything.
        You don't need to override this function, and you rarely should.

        After this function is called, and if this TrialController is connected to a Database, `bs` is sent to the Database.
        Then, `bs` will be converted into a `TrialPlayback` object, which you can then evaluate.

        You should only override this function if you want to perform an intermediary operation on the raw bytes.
        For example, you can use this function to save the raw bytes to disk.
        
        :param bs: The received message.
        """

        pass

    def on_receive_frame(self, resp: List[bytes]) -> List[Union[Command, dict]]:
        """
        This is called when the TrialController receives per-frame data.
        If your TrialController doesn't send per-frame commands, then you don't need to override this function.

        Each element in `resp` is an output data byte array except for the last element, which is the timestamp in ticks.
        To parse the timestamp, see `TDWUtils.bytes_to_time_delta(ticks)`.

        :param resp: The response from the Build.

        :return: A list of commands.
        """

        return []

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

        # Set the stop condition when receiving SIGTERM.
        loop = asyncio.get_running_loop()
        self._stop = loop.create_future()

        async with serve(self.__run, "", self._port, extra_headers={"Access-Control-Allow-Origin": "true"}):
            await self._stop

    @final
    async def __run(self, websocket: WebSocketServerProtocol) -> None:
        """
        Run the TrialController until there are no more trials to be sent.

        :param websocket: The WebSocket.
        """

        done = False
        ending_simulation: bool = False
        websocket.max_size = self.get_max_size()
        while not done:
            try:
                # Send the next trials.
                if self._send_trial_message:
                    await websocket.send(dumps(self._trial_message, cls=Encoder))
                # Send the next commands.
                else:
                    await websocket.send(dumps(self._commands, cls=Encoder))
                    self._commands.clear()
            except ConnectionClosed as e:
                print("WebSocket exception:", e)
                done = True
                continue
            # Receive end-of-trial data.
            try:
                bs: bytes = await websocket.recv()
                if not ending_simulation:
                    # This is frame data. Parse it to get commands to send on the next frame.
                    if bs[:4] == b'FRAM':
                        self._send_trial_message = False
                        self._commands = self.on_receive_frame(TrialController.__get_resp(bs))
                    # This is end-of-trial data. Parse it to get a new TrialMessage.
                    else:
                        self._send_trial_message = True
                        self.on_receive_trial_end(bs=bs)
            except ConnectionClosed as e:
                print("WebSocket exception:", e)
                done = True
                continue
            # Close the connection.
            if ending_simulation:
                done = True
                continue
            if self._send_trial_message:
                # Parse the playback.
                playback = TrialPlayback()
                playback.read(bs)
                # Send the logged end-state data.
                if self._database_socket_connected:
                    try:
                        # Send the session ID and trial data.
                        self._database_socket.send_multipart([self._session_id_bytes, bs])
                        self._database_socket.recv()
                        # Get the next trial message, which will be sent at the top of the loop.
                        self._trial_message = self.get_next_message(playback=playback)
                    except zmq.ZMQError as e:
                        print("Database exception:", e)
                        # Send a kill signal.
                        self._trial_message = TrialMessage(trials=[], adder=EndSimulation())
                else:
                    # Get the next trial message, which will be sent at the top of the loop.
                    self._trial_message = self.get_next_message(playback=playback)
                ending_simulation = isinstance(self._trial_message.adder, EndSimulation)
        # Close the log socket.
        if self._database_socket_connected:
            self._database_socket_connected = False
            self._database_socket.close()
        # Stop the server.
        self._stop.set_result(0)

    @staticmethod
    def __get_resp(bs: bytes) -> List[bytes]:
        """
        :param bs: Raw bytes from the Build.

        :return: A list of output data byte arrays.
        """

        index = 4
        # Get the number of elements.
        num_elements: int = unpack(f"<i", bs[index: index + 4])[0]
        index += 4
        num_elements_offset = num_elements * 4
        # Get the size of each element.
        element_sizes = array("i")
        element_sizes.frombytes(bs[index: index + num_elements_offset])
        index += num_elements_offset
        resp: List[bytes] = list()
        # Append each element.
        for element_size in element_sizes:
            resp.append(bs[index: index + element_size])
            index += element_size
        # Append the timestamp.
        resp.append(bs[-8:])
        return resp

    @classmethod
    def get_max_size(cls) -> int:
        """
        Override this function to set the maximum size of a WebSocket message.
        
        The default maximum size is 16777216 (16 MB).

        :return: The maximum size of a WebSocket message in bytes.
        """

        return 16777216


def run(controller: TrialController) -> None:
    """
    Run a controller. The controller will continue to try to serve data until its process is killed.

    :param controller: A TrialController.
    """

    parser = ArgumentParser(allow_abbrev=False)
    parser.add_argument("port", type=int, nargs='?', default=1337, help="The WebSocket port")
    parser.add_argument("session_id", type=int,  nargs='?', default=-1, help="The session ID")
    parser.add_argument("database_address", type=str,  nargs='?', default="", help="The database address:port")
    args, unknown = parser.parse_known_args()
    # Set the port.
    controller.set_port(port=args.port)
    # Set the session ID.
    controller.set_session_id(session_id=args.session_id)
    # Connect to the database.
    if args.database_address != "":
        controller.connect_database_socket(address=args.database_address)
    # Run the controller.
    asyncio.run(controller.main())
