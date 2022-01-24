from typing import List, Optional, Dict
import numpy as np
from tdw.add_ons.add_on import AddOn
from tdw.vr_data.rig_type import RigType
from tdw.object_data.transform import Transform
from tdw.output_data import OutputData, VRRig, StaticRigidbodies, Images


class VR(AddOn):
    """
    Add a VR rig to the scene. Make all non-kinematic objects graspable by the rig. Per-frame, update the positions of the VR rig, its hands, and its head.
    """

    """:class_var
    If image output data is enabled (see `image_passes` in the constructor), this is the ID of the VR rig's avatar.
    """
    AVATAR_ID = "vr"

    def __init__(self, rig_type: RigType = RigType.auto_hand, rig_transform_output_data: bool = True,
                 image_passes: List[str] = None):
        """
        :param rig_type: The [`RigType`](../vr_data/rig_type.md).
        :param rig_transform_output_data: If True, send [`VRRig` output data](../../api/output_data.md#VRRig) per-frame.
        :param image_passes: A list of image passes e.g. `"_img"` or `"_id"`. If None, the VR headset will still render images but it won't convert them into output data. Note: Image output data can significantly slow down a TDW simulation.
        """

        super().__init__()
        self._rig_type: RigType = rig_type
        self._set_graspable: bool = True
        self._rig_transform_output_data: bool = rig_transform_output_data
        """:field
        The [`Transform`](../object_data/transform.md) for the root rig object. If `vr_rig_output_data == False`, this is never updated.
        """
        self.rig: Transform = VR._get_empty_transform()
        """:field
        The [`Transform`](../object_data/transform.md) for the left hand. If `vr_rig_output_data == False`, this is never updated.
        """
        self.left_hand: Transform = VR._get_empty_transform()
        """:field
        The [`Transform`](../object_data/transform.md) for the right hand. If `vr_rig_output_data == False`, this is never updated.
        """
        self.right_hand: Transform = VR._get_empty_transform()
        """:field
        The [`Transform`](../object_data/transform.md) for the head. If `vr_rig_output_data == False`, this is never updated.
        """
        self.head: Transform = VR._get_empty_transform()
        """:field
        The images data as a dictionary. Key = Image pass. Value = The image. If `image_passes is None`, this is always empty.
        """
        self.images: Dict[str, np.array] = dict()
        self._image_passes: Optional[List[str]] = image_passes

    def get_initialization_commands(self) -> List[dict]:
        commands = [{"$type": "create_vr_rig",
                     "rig_type": self._rig_type.value},
                    {"$type": "send_static_rigidbodies",
                     "frequency": "once"}]
        if self._rig_transform_output_data:
            commands.append({"$type": "send_vr_rig",
                             "frequency": "always"})
        if self._image_passes is not None:
            commands.extend([{"$type": "attach_avatar_to_vr_rig",
                              "id": VR.AVATAR_ID},
                             {"$type": "set_pass_masks",
                              "pass_masks": self._image_passes,
                              "avatar_id": VR.AVATAR_ID},
                             {"$type": "send_images",
                              "frequency": "always"}])
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
            # Get image data.
            elif r_id == "imag":
                images = Images(resp[i])
                if images.get_avatar_id() == VR.AVATAR_ID:
                    self.images.clear()
                    for j in range(images.get_num_passes()):
                        self.images[images.get_pass_mask(j)] = images.get_image(j)

    def reset(self) -> None:
        """
        Reset the VR rig. Call this whenever a scene is reset.
        """

        self.initialized = False
        self._set_graspable = True

    @staticmethod
    def _get_empty_transform() -> Transform:
        """
        :return: A Transform object with all values set to 0.
        """

        return Transform(position=np.array([0, 0, 0]), rotation=np.array([0, 0, 0, 0]), forward=np.array([0, 0, 0]))
