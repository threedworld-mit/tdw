from typing import Dict, List
import numpy as np
from tdw.output_data import OutputData, Replicants, ReplicantSegmentationColors
from tdw.replicant.arm import Arm
from tdw.replicant.replicant_body_part import ReplicantBodyPart, ABLE_BODIED_BODY_PARTS, WHEELCHAIR_BODY_PARTS


class ReplicantStatic:
    """
    Static data for the Replicant.
    """

    """:class_var
    A dictionary of arms and their constituent joints.
    """
    ARM_JOINTS: Dict[Arm, List[ReplicantBodyPart]] = {Arm.left: [__b for __b in ReplicantBodyPart if __b.name.endswith("_l")],
                                                      Arm.right: [__b for __b in ReplicantBodyPart if __b.name.endswith("_r")]}

    def __init__(self, replicant_id: int, resp: List[bytes], can_walk: bool):
        """
        :param replicant_id: The ID of the Replicant.
        :param resp: The response from the build.
        :param can_walk: If True, this static data for a [`Replicant`](../add_ons/replicant.md). If False, this static data for a [`WheelchairReplicant`](../add_ons/wheelchair_replicant.md).
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
        The Replicant's segmentation color.
        """
        self.segmentation_color: np.ndarray = np.zeros(3)
        """:field
        If True, this static data for a [`Replicant`](../add_ons/replicant.md). If False, this static data for a [`WheelchairReplicant`](../add_ons/wheelchair_replicant.md).
        """
        self.can_walk: bool = can_walk
        # Get a list of body parts per Replicant.
        body_parts: List[ReplicantBodyPart] = ABLE_BODIED_BODY_PARTS.copy() if self.can_walk else WHEELCHAIR_BODY_PARTS.copy()
        # Cache the data.
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            # Get Replicants data.
            if r_id == "repl":
                replicants = Replicants(resp[i])
                for j in range(replicants.get_num()):
                    object_id = replicants.get_id(j)
                    # We found the ID of this replicant.
                    if object_id == self.replicant_id:
                        for k in range(len(body_parts)):
                            # Cache the ID.
                            self.body_parts[body_parts[k]] = replicants.get_body_part_id(j, k)
            elif r_id == "rseg":
                replicant_segmentation_colors = ReplicantSegmentationColors(resp[i])
                for j in range(replicant_segmentation_colors.get_num()):
                    object_id = replicant_segmentation_colors.get_id(j)
                    # We found the ID of this replicant.
                    if object_id == self.replicant_id:
                        self.segmentation_color = replicant_segmentation_colors.get_segmentation_color(j)
        """:field
        The Replicant's hands. Key = [`Arm`](arm.md). Value = Hand ID.
        """
        self.hands: Dict[Arm, int] = {Arm.left: self.body_parts[ReplicantBodyPart.hand_l],
                                      Arm.right: self.body_parts[ReplicantBodyPart.hand_r]}
        """:field
        Body parts by ID. Key = Object ID. Value = [`ReplicantBodyPart`](replicant_body_part.md).
        """
        self.body_parts_by_id: Dict[int, ReplicantBodyPart] = {v: k for k, v in self.body_parts.items()}
