# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.replicant_look_at_command import ReplicantLookAtCommand
from typing import Dict


class ReplicantLookAtPosition(ReplicantLookAtCommand):
    """
    Tell the Replicant to start to look at a position.
    """

    def __init__(self, id: int, position: Dict[str, float], duration: float = 0.1, set_status: bool = True):
        """
        :param id: The unique object ID.
        :param position: The position.
        :param duration: The duration of the motion.
        :param set_status: If True, when this command ends, it will set the Replicant output data's status.
        """

        super().__init__(duration=duration, set_status=set_status, id=id)
        """:field
        The position.
        """
        self.position: Dict[str, float] = position