import zmq
import json
import os
from subprocess import Popen
from typing import List, Union, Tuple, Dict
from tdw.librarian import ModelLibrarian, SceneLibrarian, MaterialLibrarian, HDRISkyboxLibrarian, \
    HumanoidAnimationLibrarian, HumanoidLibrarian, HumanoidAnimationRecord, RobotLibrarian
from tdw.backend.paths import EDITOR_LOG_PATH, PLAYER_LOG_PATH
from tdw.output_data import Version, QuitSignal
from tdw.release.build import Build
from tdw.release.pypi import PyPi
from tdw.version import __version__
from tdw.add_ons.add_on import AddOn
from tdw.physics_audio.object_audio_static import DEFAULT_OBJECT_AUDIO_STATIC_DATA
from tdw.physics_audio.audio_material import AudioMaterial
from tdw.physics_audio.audio_material_constants import STATIC_FRICTION, DYNAMIC_FRICTION, DENSITIES


class Controller:
    """
    Base class for all controllers.

    Usage:

    ```python
    from tdw.controller import Controller
    c = Controller()
    ```
    """

    MODEL_LIBRARIANS: Dict[str, ModelLibrarian] = dict()
    SCENE_LIBRARIANS: Dict[str, SceneLibrarian] = dict()
    MATERIAL_LIBRARIANS: Dict[str, MaterialLibrarian] = dict()
    HDRI_SKYBOX_LIBRARIANS: Dict[str, HDRISkyboxLibrarian] = dict()
    HUMANOID_LIBRARIANS: Dict[str, HumanoidLibrarian] = dict()
    HUMANOID_ANIMATION_LIBRARIANS: Dict[str, HumanoidAnimationLibrarian] = dict()
    ROBOT_LIBRARIANS: Dict[str, RobotLibrarian] = dict()

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        """
        Create the network socket and bind the socket to the port.

        :param port: The port number.
        :param check_version: If true, the controller will check the version of the build and print the result.
        :param launch_build: If True, automatically launch the build. If one doesn't exist, download and extract the correct version. Set this to False to use your own build, or (if you are a backend developer) to use Unity Editor.
        """

        # A list of modules that will add commands on `communicate()`.
        self.add_ons: List[AddOn] = list()

        # Compare the installed version of the tdw Python module to the latest on PyPi.
        # If there is a difference, recommend an upgrade.
        if check_version:
            self._check_pypi_version()

        # Launch the build.
        if launch_build:
            Controller.launch_build(port=port)
        context = zmq.Context()
        # noinspection PyUnresolvedReferences
        self.socket = context.socket(zmq.REP)
        self.socket.bind('tcp://*:' + str(port))

        self.socket.recv()

        # Set error handling to default values (the build will try to quit on errors and exceptions).
        # Request the version to log it and remember here if the Editor is being used.
        resp = self.communicate([{"$type": "set_error_handling"},
                                 {"$type": "send_version"},
                                 {"$type": "load_scene",
                                  "scene_name": "ProcGenScene"}])
        self._is_standalone: bool = False
        self._tdw_version: str = ""
        self._unity_version: str = ""
        for r in resp[:-1]:
            if Version.get_data_type_id(r) == "vers":
                v = Version(r)
                self._tdw_version = v.get_tdw_version()
                self._unity_version = v.get_unity_version()
                self._is_standalone = v.get_standalone()
                break
        # Compare the version of the tdw module to the build version.
        if check_version and launch_build:
            self._check_build_version()

    def communicate(self, commands: Union[dict, List[dict]]) -> list:
        """
        Send commands and receive output data in response.

        :param commands: A list of JSON commands.

        :return The output data from the build.
        """

        if isinstance(commands, dict):
            commands = [commands]

        # Append commands from each add-on.
        for m in self.add_ons:
            # Initialize an add-on.
            if not m.initialized:
                commands.extend(m.get_initialization_commands())
                m.initialized = True
            # Append the add-on's commands.
            else:
                commands.extend(m.commands)
                m.commands.clear()
        # Possibly do something with the commands about to be sent.
        for m in self.add_ons:
            m.before_send(commands)

        # Serialize the message.
        msg = [json.dumps(commands).encode('utf-8')]
        # Send the commands.
        self.socket.send_multipart(msg)
        # Receive output data.
        resp = self.socket.recv_multipart()

        # Occasionally, the build's socket will stop receiving messages.
        # If that happens, it will close the socket, create a new socket, and send a dummy output data object.
        # The ID of the dummy object is "ftre" (FailedToReceive).
        # If the controller receives the dummy object, it should re-send its commands.
        # The dummy object is always in an array: [ftre, 0]
        # This way, the controller can easily differentiate it from a response that just has the frame count.
        ftre: bool = True
        num_ftre: int = 0
        while ftre and num_ftre < 1000:
            ftre = False
            for i in range(len(resp) - 1):
                if resp[i][4:8] == b'ftre':
                    ftre = True
                    self.socket.send_multipart(msg)
                    resp = self.socket.recv_multipart()
                    num_ftre += 1
                    break
        # Tried too many times.
        if ftre:
            print("Quitting now because the controller tried too many times to resend commands to the build. "
                  "Check the build log for more info.")
            self._print_build_log()

        # Check if we've received a quit signal. If we have, check if there was an error.
        for i in range(len(resp) - 1):
            if resp[i][4:8] == b'quit':
                if not QuitSignal(resp[i]).get_ok():
                    print("The build quit due to an error. Check the build log for more info.")
                    self._print_build_log()
                break

        # Get commands per module for the next frame.
        for m in self.add_ons:
            m.on_send(resp=resp)

        # Return the output data from the build.
        return resp

    @staticmethod
    def get_add_object(model_name: str, object_id: int, position: Dict[str, float] = None, rotation: Dict[str, float] = None, library: str = "") -> dict:
        """
        Returns a valid add_object command.

        :param model_name: The name of the model.
        :param position: The position of the model. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param rotation: The starting rotation of the model, in Euler angles. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param library: The path to the records file. If left empty, the default library will be selected. See `ModelLibrarian.get_library_filenames()` and `ModelLibrarian.get_default_library()`.
        :param object_id: The ID of the new object.

        :return An add_object command that the controller can then send via [`self.communicate(commands)`](#communicate).
        """

        if library == "":
            library = "models_core.json"
        if library not in Controller.MODEL_LIBRARIANS:
            Controller.MODEL_LIBRARIANS[library] = ModelLibrarian(library)
        record = Controller.MODEL_LIBRARIANS[library].get_record(model_name)

        return {"$type": "add_object",
                "name": model_name,
                "url": record.get_url(),
                "scale_factor": record.scale_factor,
                "position": position if position is not None else {"x": 0, "y": 0, "z": 0},
                "rotation": rotation if rotation is not None else {"x": 0, "y": 0, "z": 0},
                "category": record.wcategory,
                "id": object_id}

    @staticmethod
    def get_add_physics_object(model_name: str, object_id: int, position: Dict[str, float] = None, rotation: Dict[str, float] = None, library: str = "", scale_factor: Dict[str, float] = None, kinematic: bool = False, gravity: bool = True, default_physics_values: bool = True, mass: float = 1, dynamic_friction: float = 0.3, static_friction: float = 0.3, bounciness: float = 0.7, scale_mass: bool = True) -> List[dict]:
        """
        Add an object to the scene with physics values (mass, friction coefficients, etc.).

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

        if library == "":
            library = "models_core.json"
        if library not in Controller.MODEL_LIBRARIANS:
            Controller.MODEL_LIBRARIANS[library] = ModelLibrarian(library)
        if position is None:
            position = {"x": 0, "y": 0, "z": 0}
        record = Controller.MODEL_LIBRARIANS[library].get_record(model_name)
        if position is None:
            position = {"x": 0, "y": 0, "z": 0}
        commands = [{"$type": "add_object",
                     "name": record.name,
                     "url": record.get_url(),
                     "scale_factor": record.scale_factor,
                     "position": position,
                     "category": record.wcategory,
                     "id": object_id}]
        if rotation is not None:
            # The rotation is a quaternion.
            if "w" in rotation:
                commands.append({"$type": "rotate_object_to",
                                 "rotation": rotation,
                                 "id": object_id})
            # The rotation is in Euler angles.
            else:
                commands.append({"$type": "rotate_object_to_euler_angles",
                                 "euler_angles": rotation,
                                 "id": object_id})
        commands.append({"$type": "set_kinematic_state",
                         "id": object_id,
                         "is_kinematic": kinematic,
                         "use_gravity": gravity})
        # Kinematic objects must be continuous_speculative.
        if kinematic:
            commands.append({"$type": "set_object_collision_detection_mode",
                             "id": object_id,
                             "mode": "continuous_speculative"})

        if default_physics_values:
            # Use default physics values.
            if model_name in DEFAULT_OBJECT_AUDIO_STATIC_DATA:
                mass = DEFAULT_OBJECT_AUDIO_STATIC_DATA[model_name].mass
                bounciness = DEFAULT_OBJECT_AUDIO_STATIC_DATA[model_name].bounciness
                material = DEFAULT_OBJECT_AUDIO_STATIC_DATA[model_name].material
            # Fallback: Try to derive physics values from existing data.
            else:
                if "models_full.json" not in Controller.MODEL_LIBRARIANS:
                    Controller.MODEL_LIBRARIANS["models_full.json"] = ModelLibrarian("models_full.json")
                # Get all models in the same category that have default physics values.
                records = Controller.MODEL_LIBRARIANS["models_full.json"].get_all_models_in_wnid(record.wnid)
                records = [r for r in records if not r.do_not_use and r.name != record.name and r.name in
                           DEFAULT_OBJECT_AUDIO_STATIC_DATA]
                # Fallback: Find objects with similar volume.
                if len(records) == 0:
                    records = [r for r in Controller.MODEL_LIBRARIANS["models_full.json"].records if r.name in
                               DEFAULT_OBJECT_AUDIO_STATIC_DATA and not r.do_not_use and r.name != record.name and
                               0.8 <= abs(r.volume / record.volume) <= 1.2]
                # Fallback: Select a default material and bounciness.
                if len(records) == 0:
                    material: AudioMaterial = AudioMaterial.plastic_hard
                    # Select a default bounciness.
                    bounciness: float = 0
                # Select the most common material and bounciness.
                else:
                    materials: List[AudioMaterial] = [DEFAULT_OBJECT_AUDIO_STATIC_DATA[r.name].material for r in records]
                    material: AudioMaterial = max(set(materials), key=materials.count)
                    bouncinesses = [DEFAULT_OBJECT_AUDIO_STATIC_DATA[r.name].bounciness for r in records]
                    bounciness = round(sum(bouncinesses) / len(bouncinesses), 3)
                # Derive the mass.
                mass = DENSITIES[material] * record.volume
            commands.extend([{"$type": "set_mass",
                              "mass": mass,
                              "id": object_id},
                             {"$type": "set_physic_material",
                              "dynamic_friction": DYNAMIC_FRICTION[material],
                              "static_friction": STATIC_FRICTION[material],
                              "bounciness": bounciness,
                              "id": object_id}])
        else:
            commands.extend([{"$type": "set_mass",
                              "mass": mass,
                              "id": object_id},
                             {"$type": "set_physic_material",
                              "dynamic_friction": dynamic_friction,
                              "static_friction": static_friction,
                              "bounciness": bounciness,
                              "id": object_id}])
        if scale_factor is not None:
            if scale_mass:
                commands.append({"$type": "scale_object_and_mass",
                                 "scale_factor": scale_factor,
                                 "id": object_id})
            else:
                commands.append({"$type": "scale_object",
                                 "scale_factor": scale_factor,
                                 "id": object_id})
        return commands

    @staticmethod
    def get_add_material(material_name: str, library: str = "") -> dict:
        """
        Returns a valid add_material command.

        :param material_name: The name of the material.
        :param library: The path to the records file. If left empty, the default library will be selected. See `MaterialLibrarian.get_library_filenames()` and `MaterialLibrarian.get_default_library()`.

        :return An add_material command that the controller can then send via [`self.communicate(commands)`](#communicate).
        """

        if library == "":
            library = "materials_med.json"
        if library not in Controller.MATERIAL_LIBRARIANS:
            Controller.MATERIAL_LIBRARIANS[library] = MaterialLibrarian(library)
        record = Controller.MATERIAL_LIBRARIANS[library].get_record(material_name)
        return {"$type": "add_material",
                "name": material_name,
                "url": record.get_url()}

    @staticmethod
    def get_add_scene(scene_name: str, library: str = "") -> dict:
        """
        Returns a valid add_scene command.

        :param scene_name: The name of the scene.
        :param library: The path to the records file. If left empty, the default library will be selected. See `SceneLibrarian.get_library_filenames()` and `SceneLibrarian.get_default_library()`.

        :return An add_scene command that the controller can then send via [`self.communicate(commands)`](#communicate).
        """

        if library == "":
            library = "scenes.json"
        if library not in Controller.SCENE_LIBRARIANS:
            Controller.SCENE_LIBRARIANS[library] = SceneLibrarian(library)
        record = Controller.SCENE_LIBRARIANS[library].get_record(scene_name)
        return {"$type": "add_scene",
                "name": scene_name,
                "url": record.get_url()}

    @staticmethod
    def get_add_hdri_skybox(skybox_name: str, library: str = "") -> dict:
        """
        Returns a valid add_hdri_skybox command.

        :param skybox_name: The name of the skybox.
        :param library: The path to the records file. If left empty, the default library will be selected. See `HDRISkyboxLibrarian.get_library_filenames()` and `HDRISkyboxLibrarian.get_default_library()`.

        :return An add_hdri_skybox command that the controller can then send via [`self.communicate(commands)`](#communicate).
        """

        if library == "":
            library = "hdri_skyboxes.json"
        if library not in Controller.HDRI_SKYBOX_LIBRARIANS:
            Controller.HDRI_SKYBOX_LIBRARIANS[library] = HDRISkyboxLibrarian(library)
        record = Controller.HDRI_SKYBOX_LIBRARIANS[library].get_record(skybox_name)
        return {"$type": "add_hdri_skybox",
                "name": skybox_name,
                "url": record.get_url(),
                "exposure": record.exposure,
                "initial_skybox_rotation": record.initial_skybox_rotation,
                "sun_elevation": record.sun_elevation,
                "sun_initial_angle": record.sun_initial_angle,
                "sun_intensity": record.sun_intensity}

    @staticmethod
    def get_add_humanoid(humanoid_name: str, object_id: int, position: Dict[str, float] = None, rotation: Dict[str, float] = None, library: str = "") -> dict:
        """
        Returns a valid add_humanoid command.

        :param humanoid_name: The name of the humanoid.
        :param position: The position of the humanoid.
        :param rotation: The starting rotation of the humanoid, in Euler angles.
        :param library: The path to the records file. If left empty, the default library will be selected. See `HumanoidLibrarian.get_library_filenames()` and `HumanoidLibrarian.get_default_library()`.
        :param object_id: The ID of the new object.

        :return An add_humanoid command that the controller can then send via [`self.communicate(commands)`](#communicate).
        """

        if position is None:
            position = {"x": 0, "y": 0, "z": 0}
        if rotation is None:
            rotation = {"x": 0, "y": 0, "z": 0}

        if library == "":
            library = "humanoids.json"
        if library not in Controller.HUMANOID_LIBRARIANS:
            Controller.HUMANOID_LIBRARIANS[library] = HumanoidLibrarian(library)
        record = Controller.HUMANOID_LIBRARIANS[library].get_record(humanoid_name)
        return {"$type": "add_humanoid",
                "name": humanoid_name,
                "url": record.get_url(),
                "position": position,
                "rotation": rotation,
                "id": object_id}

    @staticmethod
    def get_add_humanoid_animation(humanoid_animation_name: str, library="") -> (dict, HumanoidAnimationRecord):
        """
        Returns a valid add_humanoid_animation command and the record (which you will need to play an animation).

        :param humanoid_animation_name: The name of the animation.
        :param library: The path to the records file. If left empty, the default library will be selected. See `HumanoidAnimationLibrarian.get_library_filenames()` and `HumanoidAnimationLibrarian.get_default_library()`.

        :return An add_humanoid_animation command that the controller can then send via [`self.communicate(commands)`](#communicate).
        """

        if library == "":
            library = "humanoid_animations.json"
        if library not in Controller.HUMANOID_ANIMATION_LIBRARIANS:
            Controller.HUMANOID_ANIMATION_LIBRARIANS[library] = HumanoidAnimationLibrarian(library)
        record = Controller.HUMANOID_ANIMATION_LIBRARIANS[library].get_record(humanoid_animation_name)
        return {"$type": "add_humanoid_animation",
                "name": humanoid_animation_name,
                "url": record.get_url()}, record

    @staticmethod
    def get_add_robot(name: str, robot_id: int, position: Dict[str, float] = None, rotation: Dict[str, float] = None, library: str = "") -> dict:
        """
        Returns a valid add_robot command.

        :param name: The name of the robot.
        :param robot_id: A unique ID for the robot.
        :param position: The initial position of the robot. If None, the position will be (0, 0, 0).
        :param rotation: The initial rotation of the robot in Euler angles.
        :param library: The path to the records file. If left empty, the default library will be selected. See `RobotLibrarian.get_library_filenames()` and `RobotLibrarian.get_default_library()`.

        :return An `add_robot` command that the controller can then send via [`self.communicate(commands)`](#communicate).
        """

        if library == "":
            library = "robots.json"
        if library not in Controller.ROBOT_LIBRARIANS:
            Controller.ROBOT_LIBRARIANS[library] = RobotLibrarian(library)
        record = Controller.ROBOT_LIBRARIANS[library].get_record(name)

        if position is None:
            position = {"x": 0, "y": 0, "z": 0}
        if rotation is None:
            rotation = {"x": 0, "y": 0, "z": 0}

        assert record is not None, f"Robot metadata record not found: {name}"
        return {"$type": "add_robot",
                "id": robot_id,
                "position": position,
                "rotation": rotation,
                "name": name,
                "url": record.get_url()}

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
        raise Exception(f"Expected output data with ID version but got: " + Version.get_data_type_id(resp[0]))

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

    @staticmethod
    def launch_build(port: int = 1071) -> None:
        """
        Launch the build. If a build doesn't exist at the expected location, download one to that location.

        :param port: The socket port.
        """

        # Download the build.
        need_to_download = False
        if not Build.BUILD_PATH.exists():
            print(f"Couldn't find build at {Build.BUILD_PATH}\nDownloading now...")
            need_to_download = True
        else:
            # Check versions.
            build_version_path = Build.BUILD_ROOT_DIR.joinpath("TDW/version.txt")
            if build_version_path.exists():
                build_version = build_version_path.read_text().strip()
            else:
                build_version = "(unknown!)"
            if build_version != __version__:
                print(f"Python version is {__version__} but the build version is {build_version}.\n"
                      f"Downloading version {__version__} of the build now...")
                need_to_download = True

        # Download a new version of the build.
        if need_to_download:
            success = Build.download()
            if not success:
                print("You need to launch your own build.")
        else:
            success = True
        # Launch the build.
        if success:
            Popen([str(Build.BUILD_PATH.resolve()), "-port "+str(port)])

    def _check_build_version(self, version: str = __version__, build_version: str = None) -> None:
        """
        Check the version of the build. If there is no build, download it.
        If the build is of the wrong version, recommend an upgrade.

        :param version: The version of TDW. You can set this to an arbitrary version for testing purposes.
        :param build_version: If not None, this overrides the expected build version. Only override for debugging.
        """

        # Override the build version for testing.
        if build_version is not None:
            self._tdw_version = build_version
        print(f"Build version {self._tdw_version}\nUnity Engine {self._unity_version}\n"
              f"Python tdw module version {version}")

    def _print_build_log(self) -> None:
        """
        Print a message indicating where the build log is located.
        """

        if self._is_standalone:
            log_path = PLAYER_LOG_PATH
        else:
            log_path = EDITOR_LOG_PATH
        print(f"If the build is on the same machine as this controller, the log path is probably "
              f"{str(log_path.resolve())}")
        print(f"If the build is on a remote Linux server, the log path is probably"
              f" ~/.config/unity3d/MIT/TDW/Player.log (where ~ is your home directory)")

    @staticmethod
    def _check_pypi_version(v_installed_override: str = None, v_pypi_override: str = None) -> None:
        """
        Compare the version of the tdw Python module to the latest on PyPi.
        If there is a mismatch, offer an upgrade recommendation.

        :param v_installed_override: Override for the installed version. Change this to debug.
        :param v_pypi_override: Override for the PyPi version. Change this to debug.
        """

        # Get the version of the installed tdw module.
        installed_tdw_version = PyPi.get_installed_tdw_version()
        # Get the latest version of the tdw module on PyPi.
        pypi_version = PyPi.get_pypi_version()

        # Apply overrides
        if v_installed_override is not None:
            installed_tdw_version = v_installed_override
        if v_pypi_override is not None:
            pypi_version = v_pypi_override

        # If there is a mismatch, recommend an upgrade.
        if installed_tdw_version != pypi_version:
            # Strip the installed version of the post-release suffix (e.g. 1.6.3.4 to 1.6.3).
            stripped_installed_version = PyPi.strip_post_release(installed_tdw_version)
            # This message is here only for debugging.
            if stripped_installed_version != __version__:
                print(f"Your installed version: {stripped_installed_version} "
                      f"doesn't match tdw.version.__version__: {__version__} "
                      f"(this may be because you're using code from the tdw repo that is ahead of PyPi).")
            # Strip the latest PyPi version of the post-release suffix.
            stripped_pypi_version = PyPi.strip_post_release(pypi_version)
            print(f"You are using TDW {installed_tdw_version} but version {pypi_version} is available.")

            # If user is behind by a post release, recommend an upgrade to the latest.
            # (Example: installed version is 1.6.3.4 and PyPi version is 1.6.3.5)
            if stripped_installed_version == stripped_pypi_version:
                print(f"Upgrade to the latest version of TDW:\npip3 install tdw -U")

            # Using a version behind the latest (e.g. latest is 1.6.3 and installed is 1.6.2)
            # If the user is behind by a major or minor release, recommend either upgrading to a minor release
            # or to a major release.
            # (Example: installed version is 1.6.3.4 and PyPi version is 1.7.0.0)
            else:
                installed_major = PyPi.get_major_release(stripped_installed_version)
                pypi_minor = PyPi.get_latest_minor_release(stripped_installed_version)
                # Minor release mis-match.
                if PyPi.strip_post_release(pypi_minor) != stripped_installed_version:
                    print(f"To upgrade to the last version of 1.{installed_major}:\n"
                          f"pip3 install tdw=={pypi_minor}")
                pypi_major = PyPi.get_major_release(stripped_pypi_version)
                # Major release mis-match.
                if installed_major != pypi_major:
                    # Offer to upgrade to a major release.
                    print(f"Consider upgrading to the latest version of TDW ({stripped_pypi_version}):"
                          f"\npip3 install tdw -U")
        else:
            print("Your installed tdw Python module is up to date with PyPi.")
