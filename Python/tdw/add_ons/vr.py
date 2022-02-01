from typing import List, Dict
import numpy as np
from tdw.add_ons.add_on import AddOn
from tdw.vr_data.rig_type import RigType
from tdw.object_data.transform import Transform
from tdw.output_data import OutputData, VRRig, StaticRigidbodies


class VR(AddOn):
    """
    Add a VR rig to the scene. Make all non-kinematic objects graspable by the rig. Per-frame, update the positions of the VR rig, its hands, and its head.
    """

    """:class_var
    If image output data is enabled (see `image_passes` in the constructor), this is the ID of the VR rig's avatar.
    """
    AVATAR_ID: str = "vr"

    def __init__(self, rig_type: RigType = RigType.oculus_touch_controller_human_hands, output_data: bool = True,
                 set_graspable: bool = True, attach_avatar: bool = False, avatar_camera_width: int = 512,
                 headset_aspect_ratio: float = 0.9):
        """
        :param rig_type: The [`RigType`](../vr_data/rig_type.md).
        :param output_data: If True, send [`VRRig` output data](../../api/output_data.md#VRRig) per-frame.
        :param set_graspable: If True, set all [non-kinematic objects](../../lessons/physx/physics_objects.md) and [composite sub-objects](../../lessons/physx/composite_objects.md) as graspable by the VR rig.
        :param attach_avatar: If True, attach an [avatar](../../lessons/core_concepts/avatars.md) to the VR rig's head. Do this only if you intend to enable [image capture](../../lessons/core_concepts/images.md). The avatar's ID is `"vr"`.
        :param avatar_camera_width: The width of the avatar's camera in pixels. *This is not the same as the VR headset's screen resolution!* This only affects the avatar that is created if `attach_avatar` is `True`. Generally, you will want this to lower than the headset's actual pixel width, otherwise the framerate will be too slow.
        :param headset_aspect_ratio: The `width / height` aspect ratio of the VR headset. This is only relevant if `attach_avatar` is `True` because it is used to set the height of the output images. The default value is the correct value for all Oculus devices.
        """

        super().__init__()
        self._rig_type: RigType = rig_type
        self._set_graspable: bool = set_graspable
        self._output_data: bool = output_data
        self._attach_avatar: bool = attach_avatar
        self._avatar_camera_width: int = avatar_camera_width
        self._avatar_camera_height: int = int((1 / headset_aspect_ratio) * self._avatar_camera_width)
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

    def get_initialization_commands(self) -> List[dict]:
        commands = [{"$type": "create_vr_rig",
                     "rig_type": self._rig_type.name}]
        if self._set_graspable:
            commands.append({"$type": "send_static_rigidbodies",
                             "frequency": "once"})
        if self._output_data:
            commands.append({"$type": "send_vr_rig",
                             "frequency": "always"})
        if self._attach_avatar is not None:
            commands.extend([{"$type": "attach_avatar_to_vr_rig",
                             "id": VR.AVATAR_ID},
                             {"$type": "set_screen_size",
                              "width": self._avatar_camera_width,
                              "height": self._avatar_camera_height}])
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
                        if not static_rigidbodies.get_kinematic(j):
                            self.commands.append({"$type": "set_vr_graspable"})
                    break
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

    def teleport(self, position: Dict[str, float]) -> None:
        """
        Teleport the VR rig to a new position.

        :param position: The new position.
        """

        self.commands.append({"$type": "teleport_vr_rig",
                              "position": position})

    def rotate(self, rotation: float) -> None:
        """
        Rotate the VR rig by an angle.

        :param rotation: The angle in degrees.
        """

        self.commands.append({"$type": "rotate_vr_rig",
                              "rotation": rotation})

    def reset(self, output_data: bool = True, set_graspable: bool = True, attach_avatar: bool = False) -> None:
        """
        Reset the VR rig. Call this whenever a scene is reset.

        :param output_data: If True, send [`VRRig` output data](../../api/output_data.md#VRRig) per-frame.
        :param set_graspable: If True, set all [non-kinematic objects](../../lessons/physx/physics_objects.md) and [composite sub-objects](../../lessons/physx/composite_objects.md) as graspable by the VR rig.
        :param attach_avatar: If True, attach an [avatar](../../lessons/core_concepts/avatars.md) to the VR rig's head. Do this only if you intend to enable [image capture](../../lessons/core_concepts/images.md). The avatar's ID is `"vr"`.
        """

        self.initialized = False
        self._set_graspable = set_graspable
        self._output_data = output_data
        self._attach_avatar = attach_avatar

    @staticmethod
    def _get_empty_transform() -> Transform:
        """
        :return: A Transform object with all values set to 0.
        """

        return Transform(position=np.array([0, 0, 0]), rotation=np.array([0, 0, 0, 0]), forward=np.array([0, 0, 0]))
