from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, final
import asyncio
from websockets.server import serve
from websockets import WebSocketServerProtocol
from tdw.add_ons.add_on import AddOn
from tdw.controller import Controller
from tdw.output_data import OutputData, Version
from tdw.backend.update import Update
from tdw.librarian import SceneLibrarian


class WebGLController(ABC):
    """
    A WebGL-compatible controller. Always use this class or a subclass of it with WebGL builds instead of `Controller`.

    This is an abstract class. To use `WebGLController`, create a subclass and override `self.on_communicate(resp)`.
    """

    def __init__(self, port: int = 1071, check_version: bool = True):
        """
        :param port: The port number.
        :param check_version: If True, check if an update is available on PyPi and print the result.
        """

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
        Send commands to the WebGL build. Receive output data. Invoke `self.on_communicate(resp)`.

        :param websocket: The WebSocket.
        """

        done = False
        while not done:
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
            done, self._commands = self.on_communicate(resp=resp)

    @final
    async def main(self) -> None:
        """
        Run the WebGLController until the process is killed.
        """

        async with serve(self.communicate, "", self._port,
                         extra_headers={"Access-Control-Allow-Origin": "true"}):
            await asyncio.Future()

    @abstractmethod
    def on_communicate(self, resp: List[bytes]) -> Tuple[bool, List[dict]]:
        """
        A callback invoked after sending commands and receiving output data.

        :param resp: A list of output data frames (the response from the build).

        :return: Tuple: True if the controller is done, a list of commands that will be sent on the next frame along with commands injected from `self.add_ons`.
        """

        raise Exception()

    @staticmethod
    def get_add_physics_object(model_name: str, object_id: int, position: Dict[str, float] = None,
                               rotation: Dict[str, float] = None, library: str = "",
                               scale_factor: Dict[str, float] = None, kinematic: bool = False, gravity: bool = True,
                               default_physics_values: bool = True, mass: float = 1, dynamic_friction: float = 0.3,
                               static_friction: float = 0.3, bounciness: float = 0.7,
                               scale_mass: bool = True) -> List[dict]:
        """
        Add an object to the scene with physics values (mass, friction coefficients, etc.).

        ALWAYS call this instead of `Controller.get_add_physics_object()`.

        :param model_name: The name of the model.
        :param position: The position of the model. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param rotation: The starting rotation of the model, in Euler angles. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param library: The path to the records file. If left empty, the default library will be selected. See `ModelLibrarian.get_library_filenames()` and `ModelLibrarian.get_default_library()`.
        :param object_id: The ID of the new object.
        :param scale_factor: The [scale factor](../api/command_api.md#scale_object).
        :param kinematic: If True, the object will be [kinematic](../api/command_api.md#set_kinematic_state).
        :param gravity: If True, the object won't respond to [gravity](../api/command_api.md#set_kinematic_state).
        :param default_physics_values: If True, use default physics values. Not all objects have default physics values. To determine if object does: `has_default_physics_values = model_name in DEFAULT_OBJECT_AUDIO_STATIC_DATA`.
        :param mass: The mass of the object. Ignored if `default_physics_values == True`.
        :param dynamic_friction: The [dynamic friction](../api/command_api.md#set_physic_material) of the object. Ignored if `default_physics_values == True`.
        :param static_friction: The [static friction](../api/command_api.md#set_physic_material) of the object. Ignored if `default_physics_values == True`.
        :param bounciness: The [bounciness](../api/command_api.md#set_physic_material) of the object. Ignored if `default_physics_values == True`.
        :param scale_mass: If True, the mass of the object will be scaled proportionally to the spatial scale.

        :return: A **list** of commands to add the object and apply physics values that the controller can then send via [`self.communicate(commands)`](#communicate).
        """

        commands = Controller.get_add_physics_object(model_name=model_name, position=position, rotation=rotation,
                                                     library=library, object_id=object_id, scale_factor=scale_factor,
                                                     kinematic=kinematic, gravity=gravity,
                                                     default_physics_values=default_physics_values, mass=mass,
                                                     dynamic_friction=dynamic_friction, static_friction=static_friction,
                                                     bounciness=bounciness, scale_mass=scale_mass)
        # Set the URL.
        record = Controller.MODEL_LIBRARIANS[library].get_record(model_name)
        commands[0]["url"] = record.urls["WebGL"]
        return commands

    @staticmethod
    def get_add_scene(scene_name: str, library: str = "") -> List[dict]:
        """
        Returns a list of commands: `[add_scene, set_post_exposure]`.

        ALWAYS call this instead of `Controller.get_add_scene()`.

        :param scene_name: The name of the scene.
        :param library: The path to the records file. If left empty, the default library will be selected. See `SceneLibrarian.get_library_filenames()` and `SceneLibrarian.get_default_library()`.

        :return An add_scene command that the controller can then send via [`self.communicate(commands)`](#communicate).
        """

        if library == "":
            library = "scenes.json"
        if library not in Controller.SCENE_LIBRARIANS:
            Controller.SCENE_LIBRARIANS[library] = SceneLibrarian(library)
        record = Controller.SCENE_LIBRARIANS[library].get_record(scene_name)
        return [{"$type": "add_scene",
                 "name": scene_name,
                 "url": record.urls["WebGL"]},
                {"$type": "set_post_exposure",
                 "post_exposure": record.post_exposure}]


def run(controller: WebGLController) -> None:
    """
    Run a controller. The controller will continue to try to serve data until its process is killed.

    :param controller: A WebGL Controller.
    """

    asyncio.run(controller.main())
