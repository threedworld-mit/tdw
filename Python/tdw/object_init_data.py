from typing import Dict, List, Tuple
from tdw.librarian import ModelRecord
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller
from tdw.py_impact import AudioMaterial, PyImpact, ObjectInfo


class TransformInitData:
    """
    Basic initialization parameters for an object. Can be converted to and from a list of commands.
    """

    def __init__(self, record: ModelRecord, scale_factor: Dict[str, float] = None, position: Dict[str, float] = None,
                 rotation: Dict[str, float] = None, kinematic: bool = False, use_gravity: bool = True):
        """
        :param record: The model record.
        :param scale_factor: The [scale factor](../api/command_api.md#scale_object).
        :param position: The initial position. If None, defaults to: `{"x": 0, "y": 0, "z": 0`}.
        :param rotation: The initial rotation as a quaternion. If None, defaults to: `{"w": 1, "x": 0, "y": 0, "z": 0}`
        :param kinematic: If True, the object will be [kinematic](../api/command_api.md#set_kinematic_state).
        :param use_gravity: If True, the object won't respond to [gravity](../api/command_api.md#set_kinematic_state).
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
        self.record = record
        self.kinematic = kinematic
        self.use_gravity = use_gravity

    def get_commands(self) -> Tuple[int, List[dict]]:
        """
        :return: The ID of the object, and a list of commands to create the object.
        """

        object_id = Controller.get_unique_id()
        commands = [{"$type": "add_object",
                     "name": self.record.name,
                     "url": self.record.get_url(),
                     "scale_factor": self.record.scale_factor,
                     "position": self.position,
                     "category": self.record.wcategory,
                     "id": object_id},
                    {"$type": "rotate_object_to",
                     "rotation": self.rotation,
                     "id": object_id},
                    {"$type": "scale_object",
                     "scale_factor": self.scale_factor,
                     "id": object_id},
                    {"$type": "set_kinematic_state",
                     "id": object_id,
                     "is_kinematic": self.kinematic,
                     "use_gravity": self.use_gravity}]
        # Kinematic objects must be continuous_speculative.
        if self.kinematic:
            detection_mode = "continuous_speculative"
        else:
            detection_mode = "continuous_dynamic"
        commands.append({"$type": "set_object_collision_detection_mode",
                         "id": object_id,
                         "mode": detection_mode})
        return object_id, commands


class RigidbodyInitData(TransformInitData):
    """
    A subclass of `TransformInitData`. Includes data and commands to set the mass and physic material of the object.
    """

    def __init__(self, record: ModelRecord, mass: float, dynamic_friction: float, static_friction: float,
                 bounciness: float, scale_factor: Dict[str, float] = None, position: Dict[str, float] = None,
                 rotation: Dict[str, float] = None, kinematic: bool = False, use_gravity: bool = True):
        """
        :param record: The model record.
        :param scale_factor: The [scale factor](../api/command_api.md#scale_object).
        :param position: The initial position. If None, defaults to: `{"x": 0, "y": 0, "z": 0`}.
        :param rotation: The initial rotation as a quaternion. If None, defaults to: `{"w": 1, "x": 0, "y": 0, "z": 0}`
        :param kinematic: If True, the object will be [kinematic](../api/command_api.md#set_kinematic_state).
        :param use_gravity: If True, the object won't respond to [gravity](../api/command_api.md#set_kinematic_state).
        :param mass: The mass of the object.
        :param dynamic_friction: The [dynamic friction](../api/command_api.md#set_physic_material) of the object.
        """

        super().__init__(record=record, scale_factor=scale_factor, position=position, rotation=rotation,
                         kinematic=kinematic, use_gravity=use_gravity)
        self.mass = mass
        self.dynamic_friction = dynamic_friction
        self.static_friction = static_friction
        self.bounciness = bounciness

    def get_commands(self) -> Tuple[int, List[dict]]:
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
    Physics values are derived from the audio values.
    """

    _DYNAMIC_FRICTION = {AudioMaterial.ceramic: 0.47,
                         AudioMaterial.hardwood: 0.35,
                         AudioMaterial.wood: 0.35,
                         AudioMaterial.cardboard: 0.47,
                         AudioMaterial.glass: 0.65,
                         AudioMaterial.metal: 0.43}
    _STATIC_FRICTION = {AudioMaterial.ceramic: 0.47,
                        AudioMaterial.hardwood: 0.4,
                        AudioMaterial.wood: 0.4,
                        AudioMaterial.cardboard: 0.47,
                        AudioMaterial.glass: 0.65,
                        AudioMaterial.metal: 0.52}
    AUDIO = PyImpact.get_object_info()

    def __init__(self, record: ModelRecord, scale_factor: Dict[str, float] = None, position: Dict[str, float] = None,
                 rotation: Dict[str, float] = None, kinematic: bool = False, use_gravity: bool = True,
                 audio: ObjectInfo = None):
        """
        :param record: The model record.
        :param scale_factor: The [scale factor](../api/command_api.md#scale_object).
        :param position: The initial position. If None, defaults to: `{"x": 0, "y": 0, "z": 0`}.
        :param rotation: The initial rotation as a quaternion. If None, defaults to: `{"w": 1, "x": 0, "y": 0, "z": 0}`
        :param kinematic: If True, the object will be [kinematic](../api/command_api.md#set_kinematic_state).
        :param use_gravity: If True, the object won't respond to [gravity](../api/command_api.md#set_kinematic_state).
        :param audio: If not None, use these values instead of the default audio values.
        """

        if audio is None:
            self.audio = AudioInitData.AUDIO[record.name]
        else:
            self.audio = audio
        super().__init__(record=record, scale_factor=scale_factor, position=position, rotation=rotation,
                         kinematic=kinematic, use_gravity=use_gravity, mass=self.audio.mass,
                         dynamic_friction=AudioInitData._DYNAMIC_FRICTION[self.audio.material],
                         static_friction=AudioInitData._STATIC_FRICTION[self.audio.material],
                         bounciness=self.audio.bounciness)
