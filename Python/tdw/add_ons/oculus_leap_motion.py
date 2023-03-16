from typing import List, Dict, Callable, Optional
import numpy as np
from tdw.add_ons.vr import VR
from tdw.vr_data.rig_type import RigType
from tdw.vr_data.finger_bone import FingerBone
from tdw.object_data.transform import Transform
from tdw.output_data import OutputData, StaticRigidbodies, LeapMotion


class OculusLeapMotion(VR):
    """
    Add a VR rig to the scene that uses Leap Motion hand tracking.

    Per `communicate()` call, this add-on updates the positions of the VR rig as well as each bone of each finger, and updates per-bone collision data.
    """

    """:class_var
    The finger bones as [`FingerBone`](../vr_data/finger_bone.md) values in the order that they'll appear in this add-on's dictionaries.
    """
    BONES: List[FingerBone] = [__b for __b in FingerBone]
    """:class_var
    A dictionary. Key = [`FingerBone`](../vr_data/finger_bone.md). Value = The number degrees of freedom for that bone.
    """
    NUM_DOFS: Dict[FingerBone, int] = {__f: 3 if __f.name[-1] == "0" else 1 for __f in FingerBone if __f != FingerBone.palm}

    def __init__(self, set_graspable: bool = True, output_data: bool = True,
                 position: Dict[str, float] = None, rotation: float = 0, attach_avatar: bool = False,
                 avatar_camera_width: int = 512, headset_aspect_ratio: float = 0.9,
                 headset_resolution_scale: float = 1.0, non_graspable: List[int] = None, max_graspable_mass: float = 50,
                 min_mass: float = 1, discrete_collision_detection_mode: bool = True,
                 set_object_physic_materials: bool = True, object_static_friction: float = 1,
                 object_dynamic_friction: float = 1, object_bounciness: float = 0, time_step: float = 0.02,
                 quit_button: Optional[int] = 3):
        """
        :param set_graspable: If True, enabled "physics helpers" for all [non-kinematic objects](../../lessons/physx/physics_objects.md) that aren't listed in `non_graspable`. It's essentially not possible to grasp an object that doesn't have physics helpers.
        :param output_data: If True, send [`VRRig` output data](../../api/output_data.md#VRRig) per-frame.
        :param position: The initial position of the VR rig. If None, defaults to `{"x": 0, "y": 0, "z": 0}`
        :param rotation: The initial rotation of the VR rig in degrees.
        :param attach_avatar: If True, attach an [avatar](../../lessons/core_concepts/avatars.md) to the VR rig's head. Do this only if you intend to enable [image capture](../../lessons/core_concepts/images.md). The avatar's ID is `"vr"`.
        :param avatar_camera_width: The width of the avatar's camera in pixels. *This is not the same as the VR headset's screen resolution!* This only affects the avatar that is created if `attach_avatar` is `True`. Generally, you will want this to lower than the headset's actual pixel width, otherwise the framerate will be too slow.
        :param headset_aspect_ratio: The `width / height` aspect ratio of the VR headset. This is only relevant if `attach_avatar` is `True` because it is used to set the height of the output images. The default value is the correct value for all Oculus devices.
        :param headset_resolution_scale: The headset resolution scale controls the actual size of eye textures as a multiplier of the device's default resolution. A value greater than 1 improves image quality but at a slight performance cost. Range: 0.5 to 1.75
        :param non_graspable: A list of IDs of non-graspable objects, meaning that they don't have physics helpers (see `set_graspable`). By default, all non-kinematic objects are graspable and all kinematic objects are non-graspable. Set this to make non-kinematic objects non-graspable.
        :param max_graspable_mass: Any objects with mass greater than or equal to this value won't have physics helpers. This will prevent the hands from attempting to grasp furniture.
        :param min_mass: Unlike `max_graspable_mass`, this will actually set the mass of objects. Any object with a mass less than this value will be set to this value.
        :param discrete_collision_detection_mode: If True, the VR rig's hands and all graspable objects in the scene will be set to the `"discrete"` collision detection mode, which seems to reduce physics glitches in VR. If False, the VR rig's hands and all graspable objects will be set to the `"continuous_dynamic"` collision detection mode (the default in TDW).
        :param set_object_physic_materials: If True, set the physic material of each non-kinematic graspable object (see: `non_graspable`).
        :param object_static_friction: If `set_object_physic_materials == True`, all non-kinematic graspable object will have this static friction value.
        :param object_dynamic_friction: If `set_object_physic_materials == True`, all non-kinematic graspable object will have this dynamic friction value.
        :param object_bounciness: If `set_object_physic_materials == True`, all non-kinematic graspable object will have this bounciness value.
        :param time_step: The physics time step. Leap Motion tends to work better at this value. The TDW default is 0.01.
        :param quit_button: The button used to quit the program as an integer: 0, 1, 2, or 3. If None, no quit button will be assigned.
        """

        super().__init__(rig_type=RigType.oculus_leap_motion, output_data=output_data, position=position,
                         rotation=rotation, attach_avatar=attach_avatar, avatar_camera_width=avatar_camera_width,
                         headset_aspect_ratio=headset_aspect_ratio, headset_resolution_scale=headset_resolution_scale)
        self._set_graspable: bool = set_graspable
        if non_graspable is None:
            self._non_graspable: List[int] = list()
        else:
            self._non_graspable: List[int] = non_graspable
        self._discrete_collision_detection_mode: bool = discrete_collision_detection_mode
        """:field
        A dictionary of [`Transform`](../object_data/transform.md) for each bone in the left hand. Key = [`FingerBone`](../vr_data/finger_bone.md). Value = [`Transform`](../object_data/transform.md).
        """
        self.left_hand_transforms: Dict[FingerBone, Transform] = dict()
        """:field
        A dictionary of [`Transform`](../object_data/transform.md) for each bone on the right hand. Key = [`FingerBone`](../vr_data/finger_bone.md). Value = [`Transform`](../object_data/transform.md).
        """
        self.right_hand_transforms: Dict[FingerBone, Transform] = dict()
        """:field
        A dictionary of object IDs for each bone on the left hand. Key = [`FingerBone`](../vr_data/finger_bone.md). Value = A list of IDs of objects that the bone is colliding with.
        """
        self.left_hand_collisions: Dict[FingerBone, List[int]] = dict()
        """:field
        A dictionary of object IDs for each bone in the right hand. Key = [`FingerBone`](../vr_data/finger_bone.md). Value = A list of IDs of objects that the bone is colliding with.
        """
        self.right_hand_collisions: Dict[FingerBone, List[int]] = dict()
        """:field
        A dictionary of angles per finger bone on the left hand. Key = [`FingerBone`](../vr_data/finger_bone.md). Value = A numpy array of angles in degrees. Some bones have 3 angles and some have 1. See: `LeapMotion.NUM_DOFS`. The palm isn't in this dictionary.
        """
        self.left_hand_angles: Dict[FingerBone, np.ndarray] = dict()
        """:field
        A dictionary of angles per finger bone on the right hand. Key = [`FingerBone`](../vr_data/finger_bone.md). Value = A numpy array of angles in degrees. Some bones have 3 angles and some have 1. See: `LeapMotion.NUM_DOFS`. The palm isn't in this dictionary.
        """
        self.right_hand_angles: Dict[FingerBone, np.ndarray] = dict()
        """:field
        If True, the rig and the simulation are done. This can be useful to break a while loop in a controller. Pressing the quit button (see `quit_button`) will set this to True.
        """
        self.done = False
        self._initialize_fingers(transforms=self.left_hand_transforms, collisions=self.left_hand_collisions)
        self._initialize_fingers(transforms=self.right_hand_transforms, collisions=self.right_hand_collisions)
        self._max_graspable_mass: float = max_graspable_mass
        self._min_mass: float = min_mass
        self._set_object_physic_materials: bool = set_object_physic_materials
        self._object_static_friction: float = object_static_friction
        self._object_dynamic_friction: float = object_dynamic_friction
        self._object_bounciness: float = object_bounciness
        self._time_step: float = time_step
        self._button_callbacks: Dict[int, Callable[[], None]] = dict()
        if quit_button is not None:
            self.listen_to_button(quit_button, self._quit)

    def get_initialization_commands(self) -> List[dict]:
        commands = super().get_initialization_commands()
        commands.append({"$type": "set_time_step",
                         "time_step": self._time_step})
        if self._set_graspable:
            commands.append({"$type": "send_static_rigidbodies",
                             "frequency": "once"})
        if self._output_data:
            commands.append({"$type": "send_leap_motion",
                             "frequency": "always"})
        self._create_rig = False
        return commands

    def on_send(self, resp: List[bytes]) -> None:
        if self._set_graspable:
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                if r_id == "srig":
                    static_rigidbodies = StaticRigidbodies(resp[i])
                    for j in range(static_rigidbodies.get_num()):
                        object_id = static_rigidbodies.get_id(j)
                        kinematic = static_rigidbodies.get_kinematic(j)
                        # Ignore leap motion physics helpers.
                        mass = static_rigidbodies.get_mass(j)
                        if object_id in self._non_graspable or kinematic or mass >= self._max_graspable_mass:
                            self.commands.append({"$type": "ignore_leap_motion_physics_helpers",
                                                  "id": object_id})
                        if not kinematic:
                            # Set "discrete" collision detection mode for all non-kinematic objects.
                            if self._discrete_collision_detection_mode:
                                self.commands.append({"$type": "set_object_collision_detection_mode",
                                                      "id": object_id,
                                                      "mode": "discrete"})
                            # Set the physic material.
                            if self._set_object_physic_materials:
                                self.commands.append({"$type": "set_physic_material",
                                                      "dynamic_friction": self._object_dynamic_friction,
                                                      "static_friction": self._object_static_friction,
                                                      "bounciness": self._object_bounciness,
                                                      "id": object_id})
                            # Clamp the mass to a minimum.
                            if mass < self._min_mass:
                                self.commands.append({"$type": "set_mass",
                                                      "id": object_id,
                                                      "mass": self._min_mass})
                    break
            self._set_graspable = False
        super().on_send(resp=resp)
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "leap":
                leap_motion = LeapMotion(resp[i])
                self._set_hand(leap_motion=leap_motion,
                               hand_index=0,
                               transforms=self.left_hand_transforms,
                               collisions=self.left_hand_collisions,
                               angles=self.left_hand_angles)
                self._set_hand(leap_motion=leap_motion,
                               hand_index=1,
                               transforms=self.right_hand_transforms,
                               collisions=self.right_hand_collisions,
                               angles=self.right_hand_angles)
                # Handle button callbacks.
                for button_index in self._button_callbacks:
                    if leap_motion.get_is_button_pressed(button_index):
                        self._button_callbacks[button_index]()

    def listen_to_button(self, button: int, callback: Callable[[], None]) -> None:
        """
        Listen for when a button is pressed.

        :param button: The button as an integer: 0, 1, 2, or 3.
        :param callback: A callback function to invoke when the button is pressed. The function must have no arguments and no return value.
        """

        self._button_callbacks[button] = callback

    def reset(self, non_graspable: List[int] = None, position: Dict[str, float] = None, rotation: float = 0) -> None:
        """
        Reset the VR rig. Call this whenever a scene is reset.

        :param non_graspable: A list of IDs of non-graspable objects. By default, all non-kinematic objects are graspable and all kinematic objects are non-graspable. Set this to make non-kinematic objects non-graspable.
        :param position: The initial position of the VR rig. If None, defaults to `{"x": 0, "y": 0, "z": 0}`
        :param rotation: The initial rotation of the VR rig in degrees.
        """

        self._set_graspable = True
        if non_graspable is None:
            self._non_graspable = list()
        else:
            self._non_graspable = non_graspable
        super().reset(position=position, rotation=rotation)

    @staticmethod
    def _initialize_fingers(transforms: Dict[FingerBone, Transform], collisions: Dict[FingerBone, List[int]]) -> None:
        """
        Initialize the fingers dictionaries.

        :param transforms: The dictionary of bone transforms.
        :param collisions: The dictionary of collisions per bone.
        """

        for b in OculusLeapMotion.BONES:
            transforms[b] = Transform(position=np.zeros(shape=3),
                                      rotation=np.zeros(shape=4),
                                      forward=np.zeros(shape=3))
            collisions[b] = list()

    @staticmethod
    def _set_hand(leap_motion: LeapMotion, hand_index: int, transforms: Dict[FingerBone, Transform],
                  collisions: Dict[FingerBone, List[int]], angles: Dict[FingerBone, np.ndarray]) -> None:
        """
        :param leap_motion: The `LeapMotion` output data.
        :param hand_index: The index of the hand.
        :param transforms: The dictionary of bone transforms.
        :param collisions: The dictionary of collisions per bone.
        :param angles: The dictionary of angles per bone.
        """

        b = 0
        angle_index = 0
        max_num_collisions = leap_motion.get_num_collisions_per_bone()
        for i in range(len(OculusLeapMotion.BONES)):
            bone = OculusLeapMotion.BONES[i]
            # Set the bone transform.
            transforms[bone].position = leap_motion.get_position(hand_index, b)
            transforms[bone].rotation = leap_motion.get_rotation(hand_index, b)
            transforms[bone].forward = leap_motion.get_forward(hand_index, b)
            # Reset the collision data.
            collisions[bone].clear()
            for k in range(max_num_collisions):
                if leap_motion.get_is_collision(hand_index, b, k):
                    collisions[bone].append(leap_motion.get_collision_id(hand_index, b, k))
            # Set the angles.
            if bone != FingerBone.palm:
                dof: int = OculusLeapMotion.NUM_DOFS[bone]
                angles[bone] = leap_motion.get_angles(hand_index, angle_index, angle_index + dof)
                angle_index += dof
            b += 1

    def _quit(self) -> None:
        """
        End the simulation.
        """

        self.done = True
