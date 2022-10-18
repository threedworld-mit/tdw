from typing import List
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.image_frequency import ImageFrequency
from tdw.replicant.actions.arm_motion import ArmMotion


class ResetArm(ArmMotion):
    """
    Move arm(s) back to rest position.
    """

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        commands.extend([{"$type": "replicant_reset_arm",
                          "id": static.replicant_id,
                          "duration": self._duration,
                          "arm": arm.name} for arm in self._arms])
        return commands
