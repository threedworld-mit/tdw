from abc import ABC, abstractmethod
from typing import List, final
import asyncio
from websockets.server import serve
from websockets import WebSocketServerProtocol
from tdw.add_ons.add_on import AddOn
from tdw.controller import Controller
from tdw.output_data import OutputData, Version
from tdw.backend.update import Update


class WebGLController(ABC):
    def __init__(self, port: int = 1071, check_version: bool = True):
        if check_version:
            if Update.check_for_pypi_update():
                print("Be sure to also update any hosted WebGL builds to the latest version.")
        self._commands: List[dict] = [{"$type": "set_error_handling"},
                                      {"$type": "send_version"},
                                      {"$type": "load_scene",
                                       "scene_name": "ProcGenScene"}]
        self.add_ons: List[AddOn] = list()
        self._port: int = port
        self.__needs_version: bool = True
        self._is_standalone: bool = False
        self._tdw_version: str = ""
        self._unity_version: str = ""

    @final
    async def communicate(self, websocket: WebSocketServerProtocol) -> None:
        """
        Send commands to the WebGL build. Receive output data (`resp`). Invoke `self.on_communicate(resp)`.

        :param websocket: The WebSocket.
        """

        # Inject commands from add-ons. Convert the commands to a JSON string. Send the string.
        await websocket.send(Controller.commands_to_string(commands=self._commands, add_ons=self.add_ons))
        self._commands.clear()

        # Receive output data.
        bs: bytes = await websocket.recv()
        resp: List[bytes] = list()
        # Get the number of frames.
        num_frames = int.from_bytes(bs[0:4], byteorder="little")
        # Get the length of the frame lengths block.
        start = 4 + num_frames * 4
        for i in range(num_frames):
            # Get the length of this frame.
            frame_length = int.from_bytes(bs[i * 4 + 4: i * 4 + 8], byteorder="little")
            # Get the frame.
            frame = bs[start: start + frame_length]
            # Parse the version.
            if self.__needs_version:
                if OutputData.get_data_type_id(frame) == "vers":
                    v = Version(frame)
                    self._tdw_version = v.get_tdw_version()
                    self._unity_version = v.get_unity_version()
                    self._is_standalone = v.get_standalone()
                    self.__needs_version = False
                    break
            # Add the frame.
            resp.append(frame)
            start += frame_length
        # Get commands per add-on for the next frame.
        for m in self.add_ons:
            m.on_send(resp=resp)
        # Callback when communicate is done.
        self._commands = self.on_communicate(resp=resp)

    @final
    async def main(self) -> None:
        """
        Run the server.
        """

        async with serve(self.communicate, "", self._port,
                         extra_headers={"Access-Control-Allow-Origin": "true"}):
            await asyncio.Future()

    @abstractmethod
    def on_communicate(self, resp: List[bytes]) -> List[dict]:
        """
        A callback invoked after sending commands and receiving output data.

        :param resp: A list of output data frames (the response from the build).

        :return: A list of commands. These will be sent on the next frame along with commands injected from `self.add_ons`.
        """

        raise Exception()


def run(controller: WebGLController) -> None:
    """
    Run a controller. The controller will continue to try to serve data until its process is killed.

    :param controller: A WebGL Controller.
    """

    asyncio.run(controller.main())
