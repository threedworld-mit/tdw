from typing import Dict, List, Tuple
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller
from tdw.librarian import ModelLibrarian, ModelRecord
from tdw.py_impact import AudioMaterial, PyImpact, ObjectInfo


class TransformInitData:
    """
    Basic initialization parameters for an object. Can be converted to and from a list of commands.

    This is similar to [`Controller.get_add_object()`](controller.md) except that it includes more parameters.
    """

    LIBRARIES: Dict[str, ModelLibrarian] = dict()
    for _lib_file in ModelLibrarian.get_library_filenames():
        LIBRARIES[_lib_file] = ModelLibrarian(_lib_file)

    def __init__(self, name: str, library: str = "models_core.json", scale_factor: Dict[str, float] = None, position: Dict[str, float] = None, rotation: Dict[str, float] = None, kinematic: bool = False, gravity: bool = True):
        """
        :param name: The name of the model.
        :param library: The filename of the library containing the model's record.
        :param scale_factor: The [scale factor](../api/command_api.md#scale_object).
        :param position: The initial position. If None, defaults to: `{"x": 0, "y": 0, "z": 0`}.
        :param rotation: The initial rotation as Euler angles or a quaternion. If None, defaults to: `{"w": 1, "x": 0, "y": 0, "z": 0}`
        :param kinematic: If True, the object will be [kinematic](../api/command_api.md#set_kinematic_state).
        :param gravity: If True, the object won't respond to [gravity](../api/command_api.md#set_kinematic_state).
        """

        if position is None:
            self.position = TDWUtils.VECTOR3_ZERO
        else:
            self.position = position
        if rotation is None:
            self.rotation = {"w": 1, "x": 0, "y": 0, "z": 0}
        else:
            self.rotation = rotation
        if scale_factor is None:
            self.scale_factor = {"x": 1, "y": 1, "z": 1}
        else:
            self.scale_factor = scale_factor
        self.name = name
        self.library = library
        self.kinematic = kinematic
        self.gravity = gravity

    def get_commands(self) -> Tuple[int, List[dict]]:
        """
        :return: Tuple: The ID of the object; a list of commands to create the object: `[add_object, rotate_object_to, scale_object, set_kinematic_state, set_object_collision_detection_mode]`
        """

        record = self._get_record()

        object_id = Controller.get_unique_id()
        commands = [{"$type": "add_object",
                     "name": record.name,
                     "url": record.get_url(),
                     "scale_factor": record.scale_factor,
                     "position": self.position,
                     "category": record.wcategory,
                     "id": object_id}]
        # The rotation is a quaternion.
        if "w" in self.rotation:
            commands.append({"$type": "rotate_object_to",
                             "rotation": self.rotation,
                             "id": object_id})
        # The rotation is in Euler angles.
        else:
            commands.append({"$type": "rotate_object_to_euler_angles",
                             "euler_angles": self.rotation,
                             "id": object_id})
        commands.extend([{"$type": "scale_object",
                          "scale_factor": self.scale_factor,
                          "id": object_id},
                         {"$type": "set_kinematic_state",
                          "id": object_id,
                          "is_kinematic": self.kinematic,
                          "use_gravity": self.gravity}])
        # Kinematic objects must be continuous_speculative.
        if self.kinematic:
            commands.append({"$type": "set_object_collision_detection_mode",
                             "id": object_id,
                             "mode": "continuous_speculative"})

        return object_id, commands

    def _get_record(self) -> ModelRecord:
        """
        :return: The model metadata record for this object.
        """

        return TransformInitData.LIBRARIES[self.library].get_record(name=self.name)


class RigidbodyInitData(TransformInitData):
    """
    A subclass of `TransformInitData`. Includes data and commands to set the mass and physic material of the object.
    """

    def __init__(self, name: str, mass: float, dynamic_friction: float, static_friction: float, bounciness: float, library: str = "models_core.json", scale_factor: Dict[str, float] = None, position: Dict[str, float] = None, rotation: Dict[str, float] = None, kinematic: bool = False, gravity: bool = True):
        """
        :param name: The name of the model.
        :param library: The filename of the library containing the model's record.
        :param scale_factor: The [scale factor](../api/command_api.md#scale_object).
        :param position: The initial position. If None, defaults to: `{"x": 0, "y": 0, "z": 0`}.
        :param rotation: The initial rotation as Euler angles or a quaternion. If None, defaults to: `{"w": 1, "x": 0, "y": 0, "z": 0}`
        :param kinematic: If True, the object will be [kinematic](../api/command_api.md#set_kinematic_state).
        :param gravity: If True, the object won't respond to [gravity](../api/command_api.md#set_kinematic_state).
        :param mass: The mass of the object.
        :param dynamic_friction: The [dynamic friction](../api/command_api.md#set_physic_material) of the object.
        """

        super().__init__(name=name, library=library, scale_factor=scale_factor, position=position, rotation=rotation,
                         kinematic=kinematic, gravity=gravity)
        self.mass = mass
        self.dynamic_friction = dynamic_friction
        self.static_friction = static_friction
        self.bounciness = bounciness

    def get_commands(self) -> Tuple[int, List[dict]]:
        """
        :return: Tuple: The ID of the object; a list of commands to create the object: `[add_object, rotate_object_to, scale_object, set_kinematic_state, set_object_collision_detection_mode, set_mass, set_physic_material]`
        """

        object_id, commands = super().get_commands()
        # Set the mass and physic material.
        commands.extend([{"$type": "set_mass",
                          "mass": self.mass,
                          "id": object_id},
                         {"$type": "set_physic_material",
                          "dynamic_friction": self.dynamic_friction,
                          "static_friction": self.static_friction,
                          "bounciness": self.bounciness,
                          "id": object_id}])
        return object_id, commands


class AudioInitData(RigidbodyInitData):
    """
    A subclass of `RigidbodyInitData` that includes [audio values](py_impact.md#objectinfo).
    Physics values are derived from these audio values.
    """

    _DYNAMIC_FRICTION = {AudioMaterial.ceramic: 0.47,
                         AudioMaterial.wood_hard: 0.35,
                         AudioMaterial.wood_medium: 0.35,
                         AudioMaterial.wood_soft: 0.35,
                         AudioMaterial.cardboard: 0.45,
                         AudioMaterial.paper: 0.47,
                         AudioMaterial.glass: 0.65,
                         AudioMaterial.fabric: 0.65,
                         AudioMaterial.leather: 0.4,
                         AudioMaterial.stone: 0.7,
                         AudioMaterial.rubber: 0.75,
                         AudioMaterial.plastic_hard: 0.3,
                         AudioMaterial.plastic_soft_foam: 0.45,					 
                         AudioMaterial.metal: 0.43}
    _STATIC_FRICTION = {AudioMaterial.ceramic: 0.47,
                        AudioMaterial.wood_hard: 0.37,
                        AudioMaterial.wood_medium: 0.37,
                        AudioMaterial.wood_soft: 0.37,
                        AudioMaterial.cardboard: 0.48,
                        AudioMaterial.paper: 0.5,
                        AudioMaterial.glass: 0.68,
                        AudioMaterial.fabric: 0.67,
                        AudioMaterial.leather: 0.43,
                        AudioMaterial.stone: 0.72,
                        AudioMaterial.rubber: 0.8,
                        AudioMaterial.plastic_hard: 0.35,
                        AudioMaterial.plastic_soft_foam: 0.47,
                        AudioMaterial.metal: 0.47}
    AUDIO = PyImpact.get_object_info()

    def __init__(self, name: str, library: str = "models_core.json", scale_factor: Dict[str, float] = None, position: Dict[str, float] = None, rotation: Dict[str, float] = None, kinematic: bool = False, gravity: bool = True, audio: ObjectInfo = None):
        """
        :param name: The name of the model.
        :param library: The filename of the library containing the model's record.
        :param scale_factor: The [scale factor](../api/command_api.md#scale_object).
        :param position: The initial position. If None, defaults to: `{"x": 0, "y": 0, "z": 0`}.
        :param rotation: The initial rotation as Euler angles or a quaternion. If None, defaults to: `{"w": 1, "x": 0, "y": 0, "z": 0}`
        :param kinematic: If True, the object will be [kinematic](../api/command_api.md#set_kinematic_state).
        :param gravity: If True, the object won't respond to [gravity](../api/command_api.md#set_kinematic_state).
        :param audio: If None, derive physics data from the audio data in `PyImpact.get_object_info()` (if the object isn't in this dictionary, this constructor will throw an error). If not None, use these values instead of the default audio values.
        """

        if audio is None:
            self.audio = AudioInitData.AUDIO[name]
        else:
            self.audio = audio
        super().__init__(name=name, library=library, scale_factor=scale_factor, position=position, rotation=rotation,
                         kinematic=kinematic, gravity=gravity, mass=self.audio.mass,
                         dynamic_friction=AudioInitData._DYNAMIC_FRICTION[self.audio.material],
                         static_friction=AudioInitData._STATIC_FRICTION[self.audio.material],
                         bounciness=self.audio.bounciness)

    def get_commands(self) -> Tuple[int, List[dict]]:
        """
        :return: Tuple: The ID of the object; a list of commands to create the object: `[add_object, rotate_object_to, scale_object, set_kinematic_state, set_object_collision_detection_mode, set_mass, set_physic_material]`
        """

        return super().get_commands()
