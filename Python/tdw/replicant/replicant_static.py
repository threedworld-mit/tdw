from typing import Dict, List
from tdw.add_ons.container_manager import ContainerManager
from tdw.output_data import OutputData, Replicants
from tdw.replicant.replicant_body_part import ReplicantBodyPart, BODY_PARTS
from tdw.replicant.arm import Arm


class ReplicantStatic():
    """
    Static data for the Magnebot.

    """

    def __init__(self, replicant_id: int, container_manager: ContainerManager, resp: List[bytes]):
        """:field
        The ID of the replicant.
        """
        self.replicant_id: int = replicant_id
        """:field
        The ContainerManager of the replicant.
        """
        self.container_manager: int = container_manager
        """:field
        A dictionary of body parts. Key = The part ID. Value = The name of the part.
        """
        self.joints: Dict[int,str] = dict()
        """:field
        The name and ID of each arm joint. Key = The [`ArmJoint` enum value](arm_joint.md). Value = The object ID.
        """
        self.arm_joints: Dict[ArmJoint, int] = dict()
        """:field
        The ID of the Replicant's avatar (camera). This is used internally for API calls.
        """
        self.avatar_id: str = str(replicant_id)
        """:field
        The current primary affordance ID the replicant is reaching for/grasping when using one hand.
        """
        self.primary_target_affordance_id: int = -1
        """:field
        The current secondary affordance ID the replicant is reaching for/grasping when using two hands.
        """
        self.secondary_target_affordance_id: int = -1
        """:field
        Body parts by name. Key = The name. Value = Object ID.
        """
        self.body_parts: Dict[ReplicantBodyPart, int] = dict()

        got_data = False
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            # Get Replicants data.
            if r_id == "repl":
                replicants = Replicants(resp[i])
                for j in range(replicants.get_num()):
                    object_id = replicants.get_id(j)
                    # We found the ID of this replicant.
                    if object_id == self.replicant_id:
                        # The order of the data is always:
                        # [replicant_0, replicant_0_hand_l, replicant_0_hand_r, ... ,replicant_1, replicant_1_hand_l, ... ]
                        # So, having found the ID of this replicant, we know that the next IDs are those of its body parts.
                        for k in range(len(BODY_PARTS)):
                            # Cache the ID.
                            self.body_parts[BODY_PARTS[k]] = replicants.get_id(j + k + 1)
                        # Stop reading output data. We have what we need.
                        got_data = True
                        break
            if got_data:
                break
