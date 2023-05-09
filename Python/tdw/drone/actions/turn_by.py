from typing import List
from tdw.drone.actions.action import Action
from tdw.drone.action_status import ActionStatus
from tdw.drone.drone_dynamic import droneDynamic
from tdw.drone.image_frequency import ImageFrequency


class TurnBy(Action):
    """
    Turn by an angle.

    This is a non-animated action, meaning that the drone will immediately snap to the angle.
    """

    def __init__(self, angle: float):
        """
        :param: The angle to turn by, in degrees.
        """

        super().__init__()
        self._angle: float = angle

    def get_initialization_commands(self, resp: List[bytes], dynamic: droneDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        commands.append({"$type": "rotate_object_by",
                         "angle": self._angle,
                         "id": dynamic.drone_id,
                         "axis": "yaw",
                         "is_world": True,
                         "use_centroid": False})
        return commands

    def get_ongoing_commands(self, resp: List[bytes], dynamic: droneDynamic) -> List[dict]:
        self.status = ActionStatus.success
        return super().get_ongoing_commands(resp=resp, dynamic=dynamic)
