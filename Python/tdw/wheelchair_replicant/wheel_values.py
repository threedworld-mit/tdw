class WheelValues:
    """
    Wheel values for a move or turn action.
    """

    def __init__(self, brake_at: float, brake_torque: float, left_motor_torque: float, right_motor_torque: float,
                 steer_angle: float):
        """
        :param brake_at: The distance or angle at which to start braking.
        :param brake_torque: The torque that will be applied to the rear wheels at the end of the action.
        :param left_motor_torque: The torque that will be applied to the left rear wheel at the start of the action.
        :param right_motor_torque: The torque that will be applied to the right rear wheel at the start of the action.
        :param steer_angle: The steer angle in degrees that will applied to the front wheels at the start of the action.
        """

        """:field
        The distance or angle at which to start braking.
        """
        self.brake_at: float = brake_at
        """:field
        The torque that will be applied to the rear wheels at the end of the action.
        """
        self.brake_torque: float = brake_torque
        """:field
        The torque that will be applied to the left rear wheel at the start of the action.
        """
        self.left_motor_torque: float = left_motor_torque
        """:field
        The torque that will be applied to the right rear wheel at the start of the action.
        """
        self.right_motor_torque: float = right_motor_torque
        """:field
        The steer angle in degrees that will applied to the front wheels at the start of the action.
        """
        self.steer_angle: float = steer_angle


def get_default_values() -> WheelValues:
    """
    :return: Wheel values, all set at 0.
    """

    return WheelValues(brake_at=0, brake_torque=0, left_motor_torque=0, right_motor_torque=0, steer_angle=0)


def get_turn_values(angle: float) -> WheelValues:
    """
    :param angle: The target angle in degrees.

    :return: Wheel values for a turn action.
    """

    brake_at = abs(angle) * 0.9
    if abs(angle) < 5:
        brake_torque = 5
        outer_motor_torque = -5
        inner_motor_torque = 10
    else:
        brake_torque = 20
        outer_motor_torque = -20
        inner_motor_torque = 5
    if angle > 0:
        left_motor_torque = outer_motor_torque
        right_motor_torque = inner_motor_torque
    else:
        left_motor_torque = inner_motor_torque
        right_motor_torque = outer_motor_torque
        brake_torque *= -1
    return WheelValues(brake_at=brake_at, brake_torque=brake_torque, left_motor_torque=left_motor_torque,
                       right_motor_torque=right_motor_torque, steer_angle=angle)


def get_move_values(distance: float) -> WheelValues:
    """
    :param distance: The target distance in meters.

    :return: Wheel values for a move action.
    """

    brake_at = distance * 0.9
    if abs(distance) < 1:
        brake_torque = 5
        motor_torque = 5
    else:
        brake_torque = 10
        motor_torque = 10
    if distance < 0:
        brake_at *= -1
        brake_torque *= -1
        motor_torque *= -1
    return WheelValues(brake_at=brake_at, brake_torque=brake_torque, left_motor_torque=motor_torque,
                       right_motor_torque=motor_torque, steer_angle=0)
