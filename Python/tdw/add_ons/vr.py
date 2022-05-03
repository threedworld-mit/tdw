from abc import ABC
from typing import List, Dict
import numpy as np
from tdw.add_ons.add_on import AddOn
from tdw.vr_data.rig_type import RigType
from tdw.object_data.transform import Transform
from tdw.output_data import OutputData, VRRig


class VR(AddOn, ABC):
    """
    Add a VR rig to the scene.

    Per-frame, update the positions of the VR rig, its hands, and its head, as well as which objects it is grasping.

    Note that this is an abstract class. Different types of VR rigs use different subclasses of this add-on. See: [`OculusTouch`](oculus_touch.md).
    """

    """:class_var
    If an avatar is attached to the VR rig, this is the ID of the VR rig's avatar.
    """
    AVATAR_ID: str = "vr"

    def __init__(self, rig_type: RigType, output_data: bool = True, position: Dict[str, float] = None,
                 rotation: float = 0, attach_avatar: bool = False, avatar_camera_width: int = 512,
                 headset_aspect_ratio: float = 0.9, headset_resolution_scale: float = 1.0):
        """
        :param rig_type: The [`RigType`](../vr_data/rig_type.md).
        :param output_data: If True, send [`VRRig` output data](../../api/output_data.md#VRRig) per-frame.
        :param position: The initial position of the VR rig. If None, defaults to `{"x": 0, "y": 0, "z": 0}`
        :param rotation: The initial rotation of the VR rig in degrees.
        :param attach_avatar: If True, attach an [avatar](../../lessons/core_concepts/avatars.md) to the VR rig's head. Do this only if you intend to enable [image capture](../../lessons/core_concepts/images.md). The avatar's ID is `"vr"`.
        :param avatar_camera_width: The width of the avatar's camera in pixels. *This is not the same as the VR headset's screen resolution!* This only affects the avatar that is created if `attach_avatar` is `True`. Generally, you will want this to lower than the headset's actual pixel width, otherwise the framerate will be too slow.
        :param headset_aspect_ratio: The `width / height` aspect ratio of the VR headset. This is only relevant if `attach_avatar` is `True` because it is used to set the height of the output images. The default value is the correct value for all Oculus devices.
        :param headset_resolution_scale: The headset resolution scale controls the actual size of eye textures as a multiplier of the device's default resolution. A value greater than 1 improves image quality but at a slight performance cost. Range: 0.5 to 1.75
        """

        super().__init__()
        self._rig_type: RigType = rig_type
        self._output_data: bool = output_data
        if position is None:
            self._initial_position: Dict[str, float] = {"x": 0, "y": 0, "z": 0}
        else:
            self._initial_position = position
        self._initial_rotation: float = rotation
        self._attach_avatar: bool = attach_avatar
        self._avatar_camera_width: int = avatar_camera_width
        self._avatar_camera_height: int = int((1 / headset_aspect_ratio) * self._avatar_camera_width)
        self._headset_resolution_scale: float = headset_resolution_scale
        """:field
        The [`Transform`](../object_data/transform.md) data of the root rig object. If `output_data == False`, this is never updated.
        """
        self.rig: Transform = VR._get_empty_transform()
        """:field
        The [`Transform`](../object_data/transform.md) data of the left hand. If `output_data == False`, this is never updated.
        """
        self.left_hand: Transform = VR._get_empty_transform()
        """:field
        The [`Transform`](../object_data/transform.md) data of the right hand. If `output_data == False`, this is never updated.
        """
        self.right_hand: Transform = VR._get_empty_transform()
        """:field
        The [`Transform`](../object_data/transform.md) data of the head. If `output_data == False`, this is never updated.
        """
        self.head: Transform = VR._get_empty_transform()
        """:field
        A numpy of object IDs held by the left hand.
        """
        self.held_left: np.array = np.array([], dtype=int)
        """:field
        A numpy of object IDs held by the right hand.
        """
        self.held_right: np.array = np.array([], dtype=int)

    def get_initialization_commands(self) -> List[dict]:
        """
        This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

        :return: A list of commands that will initialize this add-on.
        """

        # Create the VR rig.
        commands = [{"$type": "create_vr_rig",
                     "sync_timestep_with_vr": True,
                     "rig_type": self._rig_type.name},
                    {"$type": "set_vr_resolution_scale",
                     "resolution_scale_factor": self._headset_resolution_scale},
                    {"$type": "set_post_process",
                     "value": False},
                    {"$type": "teleport_vr_rig",
                     "position": self._initial_position},
                    {"$type": "rotate_vr_rig_by",
                     "angle": self._initial_rotation}]
        # Send VR data per frame.
        if self._output_data:
            commands.append({"$type": "send_vr_rig",
                             "frequency": "always"})
        # Enable image capture.
        if self._attach_avatar:
            commands.extend([{"$type": "attach_avatar_to_vr_rig",
                             "id": VR.AVATAR_ID},
                             {"$type": "set_screen_size",
                              "width": self._avatar_camera_width,
                              "height": self._avatar_camera_height}])
        return commands

    def on_send(self, resp: List[bytes]) -> None:
        """
        This is called after commands are sent to the build and a response is received.

        Use this function to send commands to the build on the next frame, given the `resp` response.
        Any commands in the `self.commands` list will be sent on the next frame.

        :param resp: The response from the build.
        """

        # Get the VR rig data.
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "vrri":
                vr_rig = VRRig(resp[i])
                self.rig.position = np.array(vr_rig.get_position())
                self.rig.rotation = np.array(vr_rig.get_rotation())
                self.rig.forward = np.array(vr_rig.get_forward())
                self.left_hand.position = np.array(vr_rig.get_left_hand_position())
                self.left_hand.rotation = np.array(vr_rig.get_left_hand_rotation())
                self.left_hand.forward = np.array(vr_rig.get_left_hand_forward())
                self.right_hand.position = np.array(vr_rig.get_right_hand_position())
                self.right_hand.rotation = np.array(vr_rig.get_right_hand_rotation())
                self.right_hand.forward = np.array(vr_rig.get_right_hand_forward())
                self.head.position = np.array(vr_rig.get_head_position())
                self.head.rotation = np.array(vr_rig.get_head_rotation())
                self.head.forward = np.array(vr_rig.get_head_forward())
                self.held_left = vr_rig.get_held_left()
                self.held_right = vr_rig.get_held_right()
                break

    def set_position(self, position: Dict[str, float]) -> None:
        """
        Set the position of the VR rig.

        :param position: The new position.
        """

        self.commands.append({"$type": "teleport_vr_rig",
                              "position": position})

    def rotate_by(self, angle: float) -> None:
        """
        Rotate the VR rig by an angle.

        :param angle: The angle in degrees.
        """

        self.commands.append({"$type": "rotate_vr_rig_by",
                              "angle": angle})

    def reset(self, position: Dict[str, float] = None, rotation: float = 0) -> None:
        """
        Reset the VR rig. Call this whenever a scene is reset.

        :param position: The initial position of the VR rig. If None, defaults to `{"x": 0, "y": 0, "z": 0}`
        :param rotation: The initial rotation of the VR rig in degrees.
        """

        self.initialized = False
        self.commands.clear()
        if position is None:
            self._initial_position = {"x": 0, "y": 0, "z": 0}
        else:
            self._initial_position = position
        self._initial_rotation: float = rotation
        self.rig = VR._get_empty_transform()
        self.left_hand = VR._get_empty_transform()
        self.right_hand = VR._get_empty_transform()
        self.head = VR._get_empty_transform()
        self.held_left = np.array([], dtype=int)
        self.held_right = np.array([], dtype=int)

    @staticmethod
    def _get_empty_transform() -> Transform:
        """
        :return: A Transform object with all values set to 0.
        """

        return Transform(position=np.array([0, 0, 0]), rotation=np.array([0, 0, 0, 0]), forward=np.array([0, 0, 0]))
