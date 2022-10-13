from typing import Dict, List
from tdw.output_data import OutputData, Replicants
from tdw.agents.arm import Arm
from tdw.replicant.replicant_body_part import ReplicantBodyPart, BODY_PARTS
from tdw.relative_direction import RelativeDirection
from tdw.controller import Controller


class ReplicantStatic:
    """
    Static data for the Replicant.
    """

    """:class_var
    A dictionary of arms and their constituent joints.
    """
    ARM_JOINTS: Dict[Arm, List[ReplicantBodyPart]] = {Arm.left: [__b for __b in ReplicantBodyPart if __b.name.endswith("_l")],
                                                      Arm.right: [__b for __b in ReplicantBodyPart if __b.name.endswith("_r")]}

    def __init__(self, replicant_id: int, resp: List[bytes]):
        """
        :param replicant_id: The ID of the Replicant.
        :param resp: The response from the build.
        """

        """:field
        The ID of the Replicant.
        """
        self.replicant_id: int = replicant_id
        """:field
        The ID of the Replicant's avatar (camera). This is used internally for API calls.
        """
        self.avatar_id: str = str(replicant_id)
        """:field
        Body parts by name. Key = [`ReplicantBodyPart`](replicant_body_part.md). Value = Object ID.
        """
        self.body_parts: Dict[ReplicantBodyPart, int] = dict()
        """:field
        The IDs of overlaps used for movement. Key = [`RelativeDirection`](../relative_direction.md) (`front` or `back`). Value = The overlap ID.
        """
        self.overlap_ids: Dict[RelativeDirection, int] = {RelativeDirection.front: Controller.get_unique_id(),
                                                          RelativeDirection.back: Controller.get_unique_id()}
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
        """:field
        The Replicant's hands. Key = [`Arm`](../agents/arm.md). Value = Object ID.
        """
        self.hands: Dict[Arm, int] = {Arm.left: self.body_parts[ReplicantBodyPart.hand_l],
                                      Arm.right: self.body_parts[ReplicantBodyPart.hand_r]}
        """:field
        Body parts by ID. Key = Object ID. Value = [`ReplicantBodyPart`](replicant_body_part.md).
        """
        self.body_parts_by_id: Dict[int, ReplicantBodyPart] = {v: k for k, v in self.body_parts.items()}
