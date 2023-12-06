import zmq
import json
import os
from subprocess import Popen
from typing import List, Union, Tuple, Dict
from argparse import ArgumentParser
from tdw.librarian import ModelLibrarian, SceneLibrarian, MaterialLibrarian, HDRISkyboxLibrarian, \
    HumanoidAnimationLibrarian, HumanoidLibrarian, HumanoidAnimationRecord, RobotLibrarian, VisualEffectLibrarian, \
    DroneLibrarian, VehicleLibrarian
from tdw.backend.paths import EDITOR_LOG_PATH, PLAYER_LOG_PATH, BUILD_PATH
from tdw.output_data import Version, QuitSignal
from tdw.version import __version__
from tdw.backend.update import Update
from tdw.add_ons.add_on import AddOn
from tdw.physics_audio.object_audio_static import DEFAULT_OBJECT_AUDIO_STATIC_DATA
from tdw.physics_audio.audio_material import AudioMaterial
from tdw.physics_audio.audio_material_constants import STATIC_FRICTION, DYNAMIC_FRICTION, DENSITIES
from tdw.container_data.container_tag import ContainerTag
from tdw.container_data.box_container import BoxContainer
from tdw.container_data.sphere_container import SphereContainer
from tdw.container_data.cylinder_container import CylinderContainer


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
    VISUAL_EFFECT_LIBRARIANS: Dict[str, VisualEffectLibrarian] = dict()
    DRONE_LIBRARIANS: Dict[str, DroneLibrarian] = dict()
    VEHICLE_LIBRARIANS: Dict[str, VehicleLibrarian] = dict()

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        """
        Create the network socket and bind the socket to the port.

        :param port: The port number.
        :param check_version: If true, the controller will check the version of the build and print the result.
        :param launch_build: If True, automatically launch the build. If one doesn't exist, download and extract the correct version. Set this to False to use your own build, or (if you are a backend developer) to use Unity Editor.
        """

        # A list of modules that will add commands on `communicate()`.
        self.add_ons: List[AddOn] = list()

        # Check for updates. Download a new build if there is one.
        if check_version:
            can_launch_build = Update.check_for_update(download_build=launch_build)
        else:
            can_launch_build = False

        if not can_launch_build:
            print("You need to launch your own build.")

        # Launch the build.
        if launch_build and can_launch_build:
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
                # Insert initialization commands at the start of the list (this is rarely used).
                early_initialization_commands = m.get_early_initialization_commands()
                early_initialization_commands.reverse()
                for early_command in early_initialization_commands:
                    commands.insert(0, early_command)
                # Append initialization commands to the end of the list.
                commands.extend(m.get_initialization_commands())
                # Mark the add-on as initialized.
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
                "id": object_id,
                "affordance_points": record.affordance_points}

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
                     "id": object_id,
                     "affordance_points": record.affordance_points}]
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
        # Add container shapes.
        for container_shape in record.container_shapes:
            if isinstance(container_shape, BoxContainer):
                commands.append(Controller._add_box_container(object_id=object_id,
                                                              position=container_shape.position,
                                                              tag=container_shape.tag,
                                                              half_extents=container_shape.half_extents,
                                                              rotation=container_shape.rotation))
            elif isinstance(container_shape, CylinderContainer):
                commands.append(Controller._add_cylinder_container(object_id=object_id,
                                                                   position=container_shape.position,
                                                                   tag=container_shape.tag,
                                                                   radius=container_shape.radius,
                                                                   height=container_shape.height,
                                                                   rotation=container_shape.rotation))
            elif isinstance(container_shape, SphereContainer):
                commands.append(Controller._add_sphere_container(object_id=object_id,
                                                                 position=container_shape.position,
                                                                 tag=container_shape.tag,
                                                                 radius=container_shape.radius))
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
        :param position: The position of the humanoid. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param rotation: The starting rotation of the humanoid, in Euler angles. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
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
    def get_add_humanoid_animation(humanoid_animation_name: str, library: str = "") -> (dict, HumanoidAnimationRecord):
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
        :param position: The initial position of the robot. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param rotation: The initial rotation of the robot in Euler angles. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
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

    @staticmethod
    def get_add_visual_effect(name: str, effect_id: int, position: Dict[str, float] = None, rotation: Dict[str, float] = None, library: str = "") -> dict:
        """
        Returns a valid add_effect command.

        :param name: The name of the visual effect.
        :param effect_id: A unique ID for the visual effect.
        :param position: The initial position of the visual effect. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param rotation: The initial rotation of the visual effect in Euler angles. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param library: The path to the records file. If left empty, the default library will be selected. See `VisualEffectLibrarian.get_library_filenames()` and `VisualEffectLibrarian.get_default_library()`.

        :return An add_effect command that the controller can then send via [`self.communicate(commands)`](#communicate).
        """

        if library == "":
            library = "visual_effects.json"
        if library not in Controller.VISUAL_EFFECT_LIBRARIANS:
            Controller.VISUAL_EFFECT_LIBRARIANS[library] = VisualEffectLibrarian(library)
        if position is None:
            position = {"x": 0, "y": 0, "z": 0}
        if rotation is None:
            rotation = {"x": 0, "y": 0, "z": 0}
        record = Controller.VISUAL_EFFECT_LIBRARIANS[library].get_record(name)
        return {"$type": "add_visual_effect",
                "name": record.name,
                "id": effect_id,
                "position": position,
                "rotation": rotation,
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

        parser = ArgumentParser(allow_abbrev=False)
        parser.add_argument("--flip_images", action="store_true")
        parser.add_argument("--force_glcore42", action="store_true")
        args, unknown = parser.parse_known_args()
        build_call = [str(BUILD_PATH.resolve()), "-port " + str(port)]
        if args.flip_images:
            build_call.append("-flip_images")
        if args.force_glcore42:
            build_call.append("-force-glcore42")
        Popen(build_call)

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
    def _get_container_shape_command(command_name: str, object_id: int, position: Dict[str, float],
                                     tag: ContainerTag) -> dict:
        """
        :param command_name: The name of the command.
        :param object_id: The object ID.
        :param tag: The semantic tag.
        :param position: The local position of the container shape.

        :return: A partial command to add a container shape to an object.
        """

        # Return a partial command.
        return {"$type": command_name,
                "id": object_id,
                "container_id": int(Controller.get_unique_id()),
                "position": position,
                "tag": tag.name}

    @staticmethod
    def _add_box_container(object_id: int, position: Dict[str, float], tag: ContainerTag, half_extents: Dict[str, float],
                           rotation: Dict[str, float]) -> dict:
        """
        Add a box container shape to an object.

        :param object_id: The ID of the object.
        :param position: The position of the box relative to the parent object.
        :param tag: The box's semantic [`ContainerTag`](../container_data/container_tag.md).
        :param half_extents: The half-extents (half the scale) of the box.
        :param rotation: The rotation of the box in Euler angles relative to the parent object.

        :return: A command to add a container shape.
        """

        command = Controller._get_container_shape_command(command_name="add_box_container",
                                                          object_id=object_id,
                                                          position=position,
                                                          tag=tag)
        command["half_extents"] = half_extents
        command["rotation"] = rotation
        return command

    @staticmethod
    def _add_cylinder_container(object_id: int, position: Dict[str, float], tag: ContainerTag, radius: float,
                                height: float, rotation: Dict[str, float]) -> dict:
        """
        Add a cylinder container shape to an object.

        :param object_id: The ID of the object.
        :param position: The position of the cylinder relative to the parent object.
        :param tag: The cylinder's semantic [`ContainerTag`](../container_data/container_tag.md).
        :param radius: The radius of the cylinder.
        :param height: The height of the cylinder.
        :param rotation: The rotation of the cylinder in Euler angles relative to the parent object.

        :return: A command to add a container shape.
        """

        command = Controller._get_container_shape_command(command_name="add_cylinder_container",
                                                          object_id=object_id,
                                                          position=position,
                                                          tag=tag)
        command["radius"] = radius
        command["height"] = height
        command["rotation"] = rotation
        return command

    @staticmethod
    def _add_sphere_container(object_id: int, position: Dict[str, float], tag: ContainerTag, radius: float) -> dict:
        """
        Add a sphere container shape to an object.

        :param object_id: The ID of the object.
        :param position: The position of the sphere relative to the parent object.
        :param tag: The sphere's semantic [`ContainerTag`](../container_data/container_tag.md).
        :param radius: The radius of the sphere.

        :return: A command to add a container shape.
        """

        command = Controller._get_container_shape_command(command_name="add_sphere_container",
                                                          object_id=object_id,
                                                          position=position,
                                                          tag=tag)
        command["radius"] = radius
        return command
