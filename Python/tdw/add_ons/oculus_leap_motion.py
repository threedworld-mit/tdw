from os import urandom
from typing import List, Dict, Optional, Callable
from pathlib import Path
from pkg_resources import resource_filename
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.vr import VR
from tdw.vr_data.rig_type import RigType
from tdw.vr_data.finger_bone import FingerBone
from tdw.vr_data.finger import Finger
from tdw.replicant.arm import Arm
from tdw.object_data.transform import Transform
from tdw.output_data import OutputData, StaticRigidbodies, LeapMotion, Raycast, Overlap


class OculusLeapMotion(VR):
    """
    Add a VR rig to the scene that uses Leap Motion hand tracking.

    Per `communicate()` call, this add-on updates the positions of the VR rig as well as each bone of each finger, and updates per-bone collision data.
    """

    """:class_var
    The fingers as [`Finger`](../vr_data/finger.md) values in the order that they'll appear in this add-on's dictionaries.
    """
    FINGERS: List[Finger] = [__f for __f in Finger]
    """:class_var
    The finger bones as [`FingerBone`](../vr_data/finger_bone.md) values in the order that they'll appear in this add-on's dictionaries.
    """
    BONES: List[FingerBone] = [__b for __b in FingerBone]
    _TELEPORT_RAY_INVALID_COLOR: Dict[str, float] = {"r": 0.8, "g": 0, "b": 0, "a": 1}
    _TELEPORT_RAY_VALID_COLOR: Dict[str, float] = {"r": 0, "g": 0, "b": 0.8, "a": 1}

    def __init__(self, set_graspable: bool = True, output_data: bool = True,
                 position: Dict[str, float] = None, rotation: float = 0, attach_avatar: bool = False,
                 avatar_camera_width: int = 512, headset_aspect_ratio: float = 0.9,
                 headset_resolution_scale: float = 1.0, non_graspable: List[int] = None,
                 discrete_collision_detection_mode: bool = True):
        """
        :param set_graspable: If True, set all [non-kinematic objects](../../lessons/physx/physics_objects.md) and [composite sub-objects](../../lessons/composite_objects/overview.md) as graspable by the VR rig.
        :param output_data: If True, send [`VRRig` output data](../../api/output_data.md#VRRig) per-frame.
        :param position: The initial position of the VR rig. If None, defaults to `{"x": 0, "y": 0, "z": 0}`
        :param rotation: The initial rotation of the VR rig in degrees.
        :param attach_avatar: If True, attach an [avatar](../../lessons/core_concepts/avatars.md) to the VR rig's head. Do this only if you intend to enable [image capture](../../lessons/core_concepts/images.md). The avatar's ID is `"vr"`.
        :param avatar_camera_width: The width of the avatar's camera in pixels. *This is not the same as the VR headset's screen resolution!* This only affects the avatar that is created if `attach_avatar` is `True`. Generally, you will want this to lower than the headset's actual pixel width, otherwise the framerate will be too slow.
        :param headset_aspect_ratio: The `width / height` aspect ratio of the VR headset. This is only relevant if `attach_avatar` is `True` because it is used to set the height of the output images. The default value is the correct value for all Oculus devices.
        :param headset_resolution_scale: The headset resolution scale controls the actual size of eye textures as a multiplier of the device's default resolution. A value greater than 1 improves image quality but at a slight performance cost. Range: 0.5 to 1.75
        :param non_graspable: A list of IDs of non-graspable objects. By default, all non-kinematic objects are graspable and all kinematic objects are non-graspable. Set this to make non-kinematic objects non-graspable.
        :param discrete_collision_detection_mode: If True, the VR rig's hands and all graspable objects in the scene will be set to the `"discrete"` collision detection mode, which seems to reduce physics glitches in VR. If False, the VR rig's hands and all graspable objects will be set to the `"continuous_dynamic"` collision detection mode (the default in TDW).
        """

        super().__init__(rig_type=RigType.oculus_leap_motion_teleport, output_data=output_data, position=position,
                         rotation=rotation, attach_avatar=attach_avatar, avatar_camera_width=avatar_camera_width,
                         headset_aspect_ratio=headset_aspect_ratio, headset_resolution_scale=headset_resolution_scale)
        self._set_graspable: bool = set_graspable
        if non_graspable is None:
            self._non_graspable: List[int] = list()
        else:
            self._non_graspable: List[int] = non_graspable
        self._discrete_collision_detection_mode: bool = discrete_collision_detection_mode
        """:field
        A dictionary of [`Transform`](../object_data/transform.md) for each bone in the left hand. Key = [`Finger`](../vr_data/finger.md). Value = A dictionary. Key = [`FingerBone`](../vr_data/finger_bone.md). Value = [`Transform`](../object_data/transform.md).
        """
        self.left_hand_transforms: Dict[Finger, Dict[FingerBone, Transform]] = dict()
        """:field
        A dictionary of [`Transform`](../object_data/transform.md) for each bone in the right hand. Key = [`Finger`](../vr_data/finger.md). Value = A dictionary. Key = [`FingerBone`](../vr_data/finger_bone.md). Value = [`Transform`](../object_data/transform.md).
        """
        self.right_hand_transforms: Dict[Finger, Dict[FingerBone, Transform]] = dict()
        """:field
        A dictionary of object IDs for each bone in the left hand. Key = [`Finger`](../vr_data/finger.md). Value = A dictionary. Key = [`FingerBone`](../vr_data/finger_bone.md). Value = A list of IDs of objects that the bone is colliding with.
        """
        self.left_hand_collisions: Dict[Finger, Dict[FingerBone, List[int]]] = dict()
        """:field
        A dictionary of object IDs for each bone in the right hand. Key = [`Finger`](../vr_data/finger.md). Value = A dictionary. Key = [`FingerBone`](../vr_data/finger_bone.md). Value = A list of IDs of objects that the bone is colliding with.
        """
        self.right_finger_collisions: Dict[Finger, Dict[FingerBone, List[int]]] = dict()
        self._initialize_fingers(transforms=self.left_hand_transforms, collisions=self.left_hand_collisions)
        self._initialize_fingers(transforms=self.right_hand_transforms, collisions=self.right_finger_collisions)
        """:field
        A list of object IDs that the left palm is colliding with.
        """
        self.left_palm_collisions: List[int] = list()
        """:field
        A list of object IDs that the right palm is colliding with.
        """
        self.right_palm_collisions: List[int] = list()
        """:field
        A dictionary of predefined poses. Key = An [`Arm`](../replicant/arm.md) value for the hand. Value = A dictionary. Key = The name of the pose as a string. Value = A numpy array of the pose.
        """
        self.poses_definitions: Dict[Arm, Dict[str, np.ndarray]] = dict()
        # Load the poses.
        pose_directory = Path(resource_filename(__name__, "")).joinpath("../vr_data/leap_motion_poses").resolve()
        for arm in [Arm.left, Arm.right]:
            self.poses_definitions[arm] = dict()
            pose_hand_directory = pose_directory.joinpath(arm.name)
            if not pose_hand_directory.exists():
                continue
            for f in pose_hand_directory.iterdir():
                if f.is_file() and f.suffix == ".npy":
                    self.poses_definitions[arm][f.stem] = np.load(f)
        # A dictionary of ongoing poses. Key = An Arm value for the hand. Value = The name of the pose (can be None).
        self._poses: Dict[Arm, Optional[str]] = {Arm.left: None, Arm.right: None}
        # A dictionary of callbacks for when a pose starts.
        self._pose_enter_callbacks: Dict[Arm, Dict[str, Callable[[Arm, List[bytes]], None]]] = {Arm.left: dict(), Arm.right: dict()}
        # A dictionary of callbacks for when a pose continues.
        self._pose_stay_callbacks: Dict[Arm, Dict[str, Callable[[Arm, List[bytes]], None]]] = {Arm.left: dict(), Arm.right: dict()}
        # A dictionary of callbacks for when a pose ends.
        self._pose_exit_callbacks: Dict[Arm, Dict[str, Callable[[Arm, List[bytes]], None]]] = {Arm.left: dict(), Arm.right: dict()}
        # Local rotations are used for hand poses.
        self._finger_bone_angles: np.ndarray = np.zeros(shape=1)
        self._teleport_raycast_id: int = int.from_bytes(urandom(3), byteorder='big')
        self._can_teleport: bool = False
        self._teleport_point: np.ndarray = np.zeros(shape=3)
        self._has_teleport_line: bool = False

    def get_initialization_commands(self) -> List[dict]:
        commands = super().get_initialization_commands()
        if self._set_graspable:
            commands.append({"$type": "send_static_rigidbodies",
                             "frequency": "once"})
        if self._output_data:
            commands.append({"$type": "send_leap_motion",
                             "frequency": "always"})
        commands.append({"$type": "set_teleportation_area"})
        return commands

    def on_send(self, resp: List[bytes]) -> None:
        # Make non-kinematic objects graspable.
        if self._set_graspable:
            self._set_graspable = False
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                if r_id == "srig":
                    static_rigidbodies = StaticRigidbodies(resp[i])
                    for j in range(static_rigidbodies.get_num()):
                        object_id = static_rigidbodies.get_id(j)
                        # Make all non-kinematic objects graspable unless they are in `self._non_graspable`.
                        if object_id not in self._non_graspable:
                            self.commands.append({"$type": "set_leap_motion_graspable",
                                                  "id": object_id})
                        # Set "discrete" collision detection mode for all non-kinematic objects.
                        if self._discrete_collision_detection_mode:
                            self.commands.append({"$type": "set_object_collision_detection_mode",
                                                  "id": object_id,
                                                  "mode": "discrete"})
                    break
        super().on_send(resp=resp)
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "leap":
                leap_motion = LeapMotion(resp[i])
                self._set_hand(leap_motion=leap_motion,
                               hand_index=0,
                               transforms=self.left_hand_transforms,
                               collisions=self.left_hand_collisions,
                               palm_collisions=self.left_palm_collisions)
                self._set_hand(leap_motion=leap_motion,
                               hand_index=1,
                               transforms=self.right_hand_transforms,
                               collisions=self.right_finger_collisions,
                               palm_collisions=self.right_palm_collisions)
                self._finger_bone_angles = leap_motion._finger_bone_angles
        # Check poses.
        if self._finger_bone_angles.shape[0] == 2:
            poses: Dict[Arm, str] = dict()
            for arm in self.poses_definitions:
                for pose in self.poses_definitions[arm]:
                    d = np.linalg.norm(self._finger_bone_angles[arm.value] - self.poses_definitions[arm][pose])
                    if d < 35:
                        poses[arm] = pose
                        break
            for arm in self._poses:
                if arm in poses:
                    # Start a new pose.
                    if self._poses[arm] is None:
                        self._poses[arm] = poses[arm]
                        if self._poses[arm] in self._pose_enter_callbacks[arm]:
                            # Callback on enter.
                            self._pose_enter_callbacks[arm][self._poses[arm]](arm, resp)
                    # Continue an ongoing pose.
                    else:
                        if self._poses[arm] in self._pose_stay_callbacks[arm]:
                            # Callback on stay.
                            self._pose_stay_callbacks[arm][self._poses[arm]](arm, resp)
                else:
                    # End a pose.
                    if self._poses[arm] is not None:
                        self._poses[arm] = None
                        # Callback on exit.
                        if self._poses[arm] in self._pose_exit_callbacks[arm]:
                            self._pose_exit_callbacks[arm][self._poses[arm]](arm, resp)

    def set_pose_callbacks(self, pose: str, hand: Arm, on_enter: Callable[[Arm, List[bytes]], None] = None,
                           on_stay: Callable[[Arm, List[bytes]], None] = None, on_exit: Callable[[Arm, List[bytes]], None] = None) -> None:
        """
        Register callback methods for a pose. When the pose starts, continues, and/or exits, these methods will be invoked.

        Each of the three callbacks must have two arguments: `Arm`, i.e. the hand doing the pose, and `List[Bytes]`, i.e. the response from the build, and must return None.

        Optionally, each of the three callbacks can be None.

        :param pose: The name of the pose. See: `self.pose_definitions`.
        :param hand: The hand as an [`Arm`](../replicant/arm.md) value.
        :param on_enter: A callback method to invoke when the hand enters the pose.
        :param on_stay: A callback method to invoke when the hand stays in the pose.
        :param on_exit: A callback method to invoke when the hand exits the pose.
        """

        if on_enter is not None:
            self._pose_enter_callbacks[hand][pose] = on_enter
        if on_stay is not None:
            self._pose_stay_callbacks[hand][pose] = on_stay
        if on_exit is not None:
            self._pose_exit_callbacks[hand][pose] = on_exit

    def reset(self, non_graspable: List[int] = None, position: Dict[str, float] = None, rotation: float = 0,
              reset_pose_callbacks: bool = False) -> None:
        """
        Reset the VR rig. Call this whenever a scene is reset.

        :param non_graspable: A list of IDs of non-graspable objects. By default, all non-kinematic objects are graspable and all kinematic objects are non-graspable. Set this to make non-kinematic objects non-graspable.
        :param position: The initial position of the VR rig. If None, defaults to `{"x": 0, "y": 0, "z": 0}`
        :param rotation: The initial rotation of the VR rig in degrees.
        :param reset_pose_callbacks: If True, reset the pose callbacks. You'll need to recreate them by calling set_pose_callbacks().
        """

        self._set_graspable = True
        if non_graspable is None:
            self._non_graspable = list()
        else:
            self._non_graspable = non_graspable
        self._poses.clear()
        self._has_teleport_line = False
        self._can_teleport = False
        if reset_pose_callbacks:
            for arm in [Arm.left, Arm.right]:
                for d in [self._pose_enter_callbacks, self._pose_stay_callbacks, self._pose_exit_callbacks]:
                    d[arm].clear()
        super().reset(position=position, rotation=rotation)

    @staticmethod
    def _initialize_fingers(transforms: Dict[Finger, Dict[FingerBone, Transform]],
                            collisions: Dict[Finger, Dict[FingerBone, List[int]]]) -> None:
        """
        Initialize the fingers dictionaries.

        :param transforms: The dictionary of bone transforms.
        :param collisions: The dictionary of collisions per bone.
        """

        for f in OculusLeapMotion.FINGERS:
            transforms.update({f: dict()})
            collisions.update({f: dict()})
            for b in OculusLeapMotion.BONES:
                transforms[f].update({b: Transform(position=np.zeros(shape=3),
                                                   rotation=np.zeros(shape=4),
                                                   forward=np.zeros(shape=3))})
                collisions[f].update({b: list()})

    @staticmethod
    def _set_hand(leap_motion: LeapMotion,
                  hand_index: int,
                  transforms: Dict[Finger, Dict[FingerBone, Transform]],
                  collisions: Dict[Finger, Dict[FingerBone, List[int]]],
                  palm_collisions: List[int]) -> None:
        """
        :param leap_motion: The `LeapMotion` output data.
        :param hand_index: The index of the hand.
        :param transforms: The dictionary of bone transforms.
        :param collisions: The dictionary of collisions per bone.
        """

        b = 0
        max_num_collisions = leap_motion.get_num_collisions_per_bone()
        for i in range(len(OculusLeapMotion.FINGERS)):
            for j in range(len(OculusLeapMotion.BONES)):
                # Set the bone transform.
                transforms[OculusLeapMotion.FINGERS[i]][OculusLeapMotion.BONES[j]].position = leap_motion.get_position(hand_index, b)
                transforms[OculusLeapMotion.FINGERS[i]][OculusLeapMotion.BONES[j]].rotation = leap_motion.get_rotation(hand_index, b)
                transforms[OculusLeapMotion.FINGERS[i]][OculusLeapMotion.BONES[j]].forward = leap_motion.get_forward(hand_index, b)
                # Reset the collision data.
                collisions[OculusLeapMotion.FINGERS[i]][OculusLeapMotion.BONES[j]].clear()
                for k in range(max_num_collisions):
                    if leap_motion.get_is_collision(hand_index, b, k):
                        collisions[OculusLeapMotion.FINGERS[i]][OculusLeapMotion.BONES[j]].append(leap_motion.get_collision_id(hand_index, b, k))
                b += 1
        # Set the palm collision data.
        palm_collisions.clear()
        for i in range(max_num_collisions):
            if leap_motion.get_is_collision(hand_index, 15, i):
                palm_collisions.append(leap_motion.get_collision_id(hand_index, 15, i))

    def _cast_teleport_ray(self, hand: Arm, resp: List[bytes]) -> None:
        # TODO raycast and overlap
        raycast_hit: bool = False
        raycast_point: np.ndarray = np.zeros(shape=3)
        overlap_ids: np.ndarray = np.zeros(shape=0)
        overlap_env: bool = False
        overlap_walls: bool = False
        overlap_exists: bool = False
        # Get the raycast and overlap from the output data.
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "rayc":
                raycast: Raycast = Raycast(resp[i])
                if raycast.get_raycast_id() == self._teleport_raycast_id:
                    if raycast.get_hit() and not raycast.get_hit_object():
                        raycast_point = np.array(raycast.get_point())
                        hit = True
            elif r_id == "over":
                overlap: Overlap = Overlap(resp[i])
                if overlap.get_id() == self._teleport_raycast_id:
                    overlap_ids = overlap.get_object_ids()
                    overlap_env = overlap.get_env()
                    overlap_walls = overlap.get_walls()
        # We're casting at the floor in an empty space.
        if raycast_hit and raycast_point[1] <= 0.05 and overlap_env and not overlap_walls and len(overlap_ids) == 0:
            self._can_teleport = True
            self._teleport_point = raycast_point
            color = OculusLeapMotion._TELEPORT_RAY_VALID_COLOR
        # We either aren't casting or we aren't casting at a good spot.
        else:
            self._can_teleport = False
            color = OculusLeapMotion._TELEPORT_RAY_INVALID_COLOR
        # Get the origin point.
        hand_position: np.ndarray = self.left_hand.position if hand == Arm.left else self.right_hand.position
        # The raycast exists and hit something.
        if hit:
            points = [TDWUtils.array_to_vector3(hand_position), TDWUtils.array_to_vector3(raycast_point)]
            # Update an existing line.
            if self._has_teleport_line:
                self.commands.extend([{"$type": "set_line_renderer_points",
                                       "id": self._teleport_raycast_id,
                                       "points": points},
                                      {"$type": "set_line_renderer_color",
                                       "start_color": color,
                                       "end_color": color,
                                       "points": points,
                                       "id": self._teleport_raycast_id}])
            # Create a new line.
            else:
                self._has_teleport_line = True
                self.commands.append({"$type": "add_line_renderer",
                                      "points": points,
                                      "start_color": color,
                                      "end_color": color,
                                      "id": self._teleport_raycast_id})
        # Cast a ray and an overlap.


