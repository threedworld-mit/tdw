from typing import List
import numpy as np
from tdw.add_ons.add_on import AddOn
from tdw.vr_data.rig_type import RigType
from tdw.object_data.transform import Transform
from tdw.output_data import OutputData, VRRig, StaticRigidbodies


class VR(AddOn):
    """
    Add a VR rig to the scene. Make all non-kinematic objects graspable by the rig. Per-frame, update the positions of the VR rig, its hands, and its head.
    """

    def __init__(self, rig_type: RigType = RigType.auto_hand):
        """
        :param rig_type: The [`RigType`](../vr_data/rig_type.md).
        """

        super().__init__()
        self._rig_type: RigType = rig_type
        self._set_graspable: bool = True
        """:field
        The [`Transform`](../object_data/transform.md) for the root rig object.
        """
        self.rig: Transform = VR._get_empty_transform()
        """:field
        The [`Transform`](../object_data/transform.md) for the left hand.
        """
        self.left_hand: Transform = VR._get_empty_transform()
        """:field
        The [`Transform`](../object_data/transform.md) for the right hand.
        """
        self.right_hand: Transform = VR._get_empty_transform()
        """:field
        The [`Transform`](../object_data/transform.md) for the head.
        """
        self.head: Transform = VR._get_empty_transform()

    def get_initialization_commands(self) -> List[dict]:
        return [{"$type": "create_vr_rig",
                 "rig_type": self._rig_type.value},
                {"$type": "send_vr_rig",
                 "frequency": "always"},
                {"$type": "send_static_rigidbodies",
                 "frequency": "once"}]

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
        # Update the rig data.
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
                break

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
