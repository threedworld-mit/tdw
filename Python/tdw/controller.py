import zmq
import json
import os
from typing import List, Union, Optional, Tuple
from tdw.librarian import ModelLibrarian, SceneLibrarian, MaterialLibrarian, HDRISkyboxLibrarian, \
    HumanoidAnimationLibrarian, HumanoidLibrarian, HumanoidAnimationRecord
from tdw.output_data import Version
from tdw.version import __version__, last_stable_release


class Controller(object):
    """
    Base class for all controllers.

    Usage:

    ```python
    from tdw.controller import Controller
    c = Controller()
    c.start()
    ```
    """

    def __init__(self, port: int = 1071, check_version: bool = True):
        """
        Create the network socket and bind the socket to the port.

        :param port: The port number.
        :param check_version: If true, the controller will check the version of the build and print the result.
        """

        context = zmq.Context()

        self.socket = context.socket(zmq.REP)
        self.socket.bind('tcp://*:' + str(port))

        self.socket.recv()

        self.model_librarian: Optional[ModelLibrarian] = None
        self.scene_librarian: Optional[SceneLibrarian] = None
        self.material_librarian: Optional[MaterialLibrarian] = None
        self.hdri_skybox_librarian: Optional[HDRISkyboxLibrarian] = None
        self.humanoid_librarian: Optional[HumanoidLibrarian] = None
        self.humanoid_animation_librarian: Optional[HumanoidAnimationLibrarian] = None

        # Compare the version of the tdw module to the build version.
        if check_version:
            tdw_version, unity_version = self.get_version()
            print(f"Build version {tdw_version}\nUnity Engine {unity_version}\nPython tdw module version {__version__}")
            if __version__ != tdw_version:
                print("WARNING! Your Python code is not the same version as the build. They might not be compatible.")
                print("Either use the latest prerelease build, or use the last stable release via:\n")
                print("git checkout v" + last_stable_release)

    def communicate(self, commands: Union[dict, List[dict]]) -> list:
        """
        Send commands and receive output data in response.

        :param commands: A list of JSON commands.

        :return The output data from the build.
        """

        if not isinstance(commands, list):
            commands = [commands]

        self.socket.send_multipart([json.dumps(commands).encode('utf-8')])

        return self.socket.recv_multipart()

    def start(self, scene="ProcGenScene") -> None:
        """
        Init TDW.

        :param scene: The scene to load.
        """

        self.communicate([{"$type": "load_scene", "scene_name": scene}])

    def get_add_object(self, model_name: str, object_id: int, position={"x": 0, "y": 0, "z": 0}, rotation={"x": 0, "y": 0, "z": 0}, library: str = "") -> dict:
        """
        Returns a valid add_object command.

        :param model_name: The name of the model.
        :param position: The position of the model.
        :param rotation: The starting rotation of the model, in Euler angles.
        :param library: The path to the records file. If left empty, the default library will be selected. See `ModelLibrarian.get_library_filenames()` and `ModelLibrarian.get_default_library()`.
        :param object_id: The ID of the new object.

        :return An add_object command that the controller can then send.
        """

        if self.model_librarian is None or (library != "" and self.model_librarian.library != library):
            self.model_librarian = ModelLibrarian(library=library)

        record = self.model_librarian.get_record(model_name)

        return {"$type": "add_object",
                "name": model_name,
                "url": record.get_url(),
                "scale_factor": record.scale_factor,
                "position": position,
                "rotation": rotation,
                "category": record.wcategory,
                "id": object_id}

    def get_add_material(self, material_name: str, library: str = "") -> dict:
        """
        Returns a valid add_material command.

        :param material_name: The name of the material.
        :param library: The path to the records file. If left empty, the default library will be selected. See `MaterialLibrarian.get_library_filenames()` and `MaterialLibrarian.get_default_library()`.

        :return An add_material command that the controller can then send.
        """

        if self.material_librarian is None:
            self.material_librarian = MaterialLibrarian(library=library)

        record = self.material_librarian.get_record(material_name)
        return {"$type": "add_material",
                "name": material_name,
                "url": record.get_url()}

    def get_add_scene(self, scene_name: str, library: str = "") -> dict:
        """
        Returns a valid add_scene command.

        :param scene_name: The name of the scene.
        :param library: The path to the records file. If left empty, the default library will be selected. See `SceneLibrarian.get_library_filenames()` and `SceneLibrarian.get_default_library()`.

        :return An add_scene command that the controller can then send.
        """

        if self.scene_librarian is None:
            self.scene_librarian = SceneLibrarian(library=library)

        record = self.scene_librarian.get_record(scene_name)
        return {"$type": "add_scene",
                "name": scene_name,
                "url": record.get_url()}

    def get_add_hdri_skybox(self, skybox_name: str, library: str = "") -> dict:
        """
        Returns a valid add_hdri_skybox command.

        :param skybox_name: The name of the skybox.
        :param library: The path to the records file. If left empty, the default library will be selected. See `HDRISkyboxLibrarian.get_library_filenames()` and `HDRISkyboxLibrarian.get_default_library()`.

        :return An add_hdri_skybox command that the controller can then send.
        """

        if self.hdri_skybox_librarian is None:
            self.hdri_skybox_librarian = HDRISkyboxLibrarian(library=library)

        record = self.hdri_skybox_librarian.get_record(skybox_name)
        return {"$type": "add_hdri_skybox",
                "name": skybox_name,
                "url": record.get_url(),
                "exposure": record.exposure,
                "initial_skybox_rotation": record.initial_skybox_rotation,
                "sun_elevation": record.sun_elevation,
                "sun_initial_angle": record.sun_initial_angle,
                "sun_intensity": record.sun_intensity}

    def get_add_humanoid(self, humanoid_name: str, object_id: int, position={"x": 0, "y": 0, "z": 0}, rotation={"x": 0, "y": 0, "z": 0}, library: str ="") -> dict:
        """
        Returns a valid add_humanoid command.

        :param humanoid_name: The name of the humanoid.
        :param position: The position of the humanoid.
        :param rotation: The starting rotation of the humanoid, in Euler angles.
        :param library: The path to the records file. If left empty, the default library will be selected. See `HumanoidLibrarian.get_library_filenames()` and `HumanoidLibrarian.get_default_library()`.
        :param object_id: The ID of the new object.

        :return An add_humanoid command that the controller can then send.
        """

        if self.humanoid_librarian is None or (library != "" and self.humanoid_librarian.library != library):
            self.humanoid_librarian = HumanoidLibrarian(library=library)

        record = self.humanoid_librarian.get_record(humanoid_name)

        return {"$type": "add_humanoid",
                "name": humanoid_name,
                "url": record.get_url(),
                "position": position,
                "rotation": rotation,
                "id": object_id}

    def get_add_humanoid_animation(self, humanoid_animation_name: str, library="") -> (dict, HumanoidAnimationRecord):
        """
        Returns a valid add_humanoid_animation command and the record (which you will need to play an animation).

        :param humanoid_animation_name: The name of the animation.
        :param library: The path to the records file. If left empty, the default library will be selected. See `HumanoidAnimationLibrarian.get_library_filenames()` and `HumanoidAnimationLibrarian.get_default_library()`.

        return An add_humanoid_animation command that the controller can then send.
        """

        if self.humanoid_animation_librarian is None:
            self.humanoid_animation_librarian = HumanoidAnimationLibrarian(library=library)

        record = self.humanoid_animation_librarian.get_record(humanoid_animation_name)
        return {"$type": "add_humanoid_animation",
                "name": humanoid_animation_name,
                "url": record.get_url()}, record

    def load_streamed_scene(self, scene="tdw_room_2018") -> None:
        """
        Load a streamed scene. This is equivalent to: `c.communicate(c.get_add_scene(scene))`

        :param scene: The name of the streamed scene.
        """

        self.communicate(self.get_add_scene(scene))

    def add_object(self, model_name: str, position={"x": 0, "y": 0, "z": 0}, rotation={"x": 0, "y": 0, "z": 0}, library: str= "") -> int:
        """
        Add a model to the scene. This is equivalent to: `c.communicate(c.get_add_object())`

        :param model_name: The name of the model.
        :param position: The position of the model.
        :param rotation: The starting rotation of the model, in Euler angles.
        :param library: The path to the records file. If left empty, the default library will be selected. See `ModelLibrarian.get_library_filenames()` and `ModelLibrarian.get_default_library()`.

        :return The ID of the new object.
        """

        object_id = Controller.get_unique_id()
        self.communicate(self.get_add_object(model_name, object_id, position, rotation, library))

        return object_id

    def get_version(self) -> Tuple[str, str]:
        """
        Send a send_version command to the build.

        :return The TDW version and the Unity Engine version.
        """

        resp = self.communicate({"$type": "send_version"})
        for r in resp[:-1]:
            if Version.get_data_type_id(r) == "vers":
                v = Version(r)
                return v.get_tdw_version(), v.get_unity_version()
        if len(resp) == 1:
            raise Exception("Tried receiving version output data but didn't receive anything!")
        raise Exception(f"Expected output data with ID vers but got: " + Version.get_data_type_id(resp[0]))

    @staticmethod
    def get_unique_id() -> int:
        """
        Generate a unique integer. Useful when creating objects.

        :return The new unique ID.
        """

        return int.from_bytes(os.urandom(3), byteorder='big')

    @staticmethod
    def get_frame(frame: bytes) -> int:
        """
        Converts the frame byte array to an integer.

        :param frame: The frame as bytes.

        :return The frame as an integer.
        """

        return int.from_bytes(frame, byteorder='big')
