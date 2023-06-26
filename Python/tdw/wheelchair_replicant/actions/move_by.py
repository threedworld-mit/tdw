from typing import Optional
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.actions.action import Action
from tdw.replicant.collision_detection import CollisionDetection


class MoveBy(Action):
    def __init__(self, distance: float, motor_torque: float, brake_torque: float, brake_at: float,
                 dynamic: ReplicantDynamic, collision_detection: CollisionDetection,
                 previous: Optional[Action], reset_arms: bool, reset_arms_duration: float,
                 scale_reset_arms_duration: bool, arrived_at: float):
        """
        :param distance: The target distance. If less than 0, the Replicant will walk backwards.
        :param dynamic: The [`ReplicantDynamic`](../replicant_dynamic.md) data that changes per `communicate()` call.
        :param collision_detection: The [`CollisionDetection`](../collision_detection.md) rules.
        :param previous: The previous action, if any.
        :param reset_arms: If True, reset the arms to their neutral positions while beginning the walk cycle.
        :param reset_arms_duration: The speed at which the arms are reset in seconds.
        :param scale_reset_arms_duration: If True, `reset_arms_duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        :param arrived_at: If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        :param max_walk_cycles: The walk animation will loop this many times maximum. If by that point the Replicant hasn't reached its destination, the action fails.
        """