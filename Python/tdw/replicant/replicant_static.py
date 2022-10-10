from typing import Dict, List
from tdw.output_data import OutputData, Replicants
from tdw.replicant.replicant_body_part import ReplicantBodyPart, BODY_PARTS


class ReplicantStatic:
    """
    Static data for the Replicant.

    """

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
