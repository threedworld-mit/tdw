from typing import List
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.image_frequency import ImageFrequency
from tdw.replicant.actions.arm_motion import ArmMotion


class ResetArm(ArmMotion):
    """
    Move arm(s) back to rest position(s). One or both arms can be reset at the same time.

    The Replicant's arm(s) will continuously over multiple `communicate()` calls move until either the motion is complete or the arm collides with something (see `self.collision_detection`).

    - The collision detection will respond normally to walls, objects, obstacle avoidance, etc.
    - If `self.collision_detection.previous_was_same == True`, and if the previous action was a subclass of `ArmMotion`, and it ended in a collision, this action ends immediately.
    """

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        commands.extend([{"$type": "replicant_reset_arm" if static.can_walk else "wheelchair_replicant_reset_arm",
                          "id": static.replicant_id,
                          "duration": self.duration,
                          "arm": arm.name} for arm in self.arms])
        return commands
