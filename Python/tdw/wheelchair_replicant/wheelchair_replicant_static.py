from typing import List
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_body_part import ReplicantBodyPart, WHEELCHAIR_BODY_PARTS


class WheelchairReplicantStatic(ReplicantStatic):
    """
    Static data for the WheelchairReplicant.
    """

    def get_body_parts(self) -> List[ReplicantBodyPart]:
        return WHEELCHAIR_BODY_PARTS
