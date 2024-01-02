# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.magnebot_wheels_command import MagnebotWheelsCommand
from typing import Dict


class SetMagnebotWheelsDuringMove(MagnebotWheelsCommand):
    """
    Set the friction coefficients of the Magnebot's wheels during a move_by() or move_to() action, given a target position. The friction coefficients will increase as the Magnebot approaches the target position and the command will announce if the Magnebot arrives at the target position.
    """

    def __init__(self, origin: Dict[str, float], position: Dict[str, float], brake_distance: float = 0.1, arrived_at: float = 0.01, minimum_friction: float = 0.05, maximum_friction: float = 1, id: int = 0):
        """
        :param origin: The origin of the Magnebot at the start of the action (not its current position).
        :param position: The target destination of the Magnebot.
        :param brake_distance: The distance at which the Magnebot should start to brake, in meters.
        :param arrived_at: The threshold for determining whether the Magnebot is at the target.
        :param minimum_friction: The minimum friction coefficient for the wheels. The default value (0.05) is also the default friction coefficient of the wheels.
        :param maximum_friction: The maximum friction coefficient for the wheels when slowing down.
        :param id: The ID of the robot in the scene.
        """

        super().__init__(arrived_at=arrived_at, minimum_friction=minimum_friction, maximum_friction=maximum_friction, id=id)
        """:field
        The target destination of the Magnebot.
        """
        self.position: Dict[str, float] = position
        """:field
        The origin of the Magnebot at the start of the action (not its current position).
        """
        self.origin: Dict[str, float] = origin
        """:field
        The distance at which the Magnebot should start to brake, in meters.
        """
        self.brake_distance: float = brake_distance
