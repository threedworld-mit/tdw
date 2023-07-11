from tdw.tdw_utils import TDWUtils


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


def get_turn_values(angle: float, arrived_at: float) -> WheelValues:
    """
    :param angle: The target angle in degrees.
    :param arrived_at: The arrived-at threshold in degrees.

    :return: Wheel values for a turn action.
    """

    brake_at = abs(angle) - arrived_at / 2
    brake_torque = 5
    a = abs(angle)
    steer_angle = angle
    if a <= 5:
        outer_motor_torque = 11
        inner_motor_torque = -12
    # Lerp between values that are known to be good at certain angles.
    elif a <= 15:
        t = TDWUtils.inv_lerp(a=5, b=15, v=a)
        outer_motor_torque = TDWUtils.lerp(a=11, b=12, t=t)
        inner_motor_torque = TDWUtils.lerp(a=-17, b=-12, t=1 - t)
    elif a <= 25:
        t = 1 - TDWUtils.inv_lerp(a=15, b=25, v=a)
        outer_motor_torque = TDWUtils.lerp(a=11, b=12, t=t)
        inner_motor_torque = TDWUtils.lerp(a=-19, b=-17, t=t)
    elif a <= 45:
        t = 1 - TDWUtils.inv_lerp(a=25, b=45, v=a)
        outer_motor_torque = TDWUtils.lerp(a=10, b=11, t=t)
        inner_motor_torque = TDWUtils.lerp(a=-20, b=-19, t=t)
    elif a <= 90:
        t = TDWUtils.inv_lerp(a=45, b=90, v=a)
        outer_motor_torque = TDWUtils.lerp(a=10, b=19, t=t)
        inner_motor_torque = TDWUtils.lerp(a=-20, b=-18, t=t)
    elif a <= 120:
        t = TDWUtils.inv_lerp(a=90, b=120, v=a)
        outer_motor_torque = TDWUtils.lerp(a=19, b=20, t=t)
        inner_motor_torque = TDWUtils.lerp(a=-18, b=-10, t=1 - t)
    # Use the values for 120 degrees.
    else:
        outer_motor_torque = 20
        inner_motor_torque = -10
        # Clamp the steer angle. It's unclear why we need to do this.
        max_steer_angle = 150
        if a > max_steer_angle:
            steer_angle = max_steer_angle
            if angle < 0:
                steer_angle *= -1
    # Map outer/inner to left/right.
    if angle > 0:
        left_motor_torque = outer_motor_torque
        right_motor_torque = inner_motor_torque
    else:
        left_motor_torque = inner_motor_torque
        right_motor_torque = outer_motor_torque
    return WheelValues(brake_at=brake_at, brake_torque=brake_torque, left_motor_torque=left_motor_torque,
                       right_motor_torque=right_motor_torque, steer_angle=steer_angle)


def get_move_values(distance: float) -> WheelValues:
    """
    :param distance: The target distance in meters.

    :return: Wheel values for a move action.
    """

    d = abs(distance)
    brake_at = d * 0.9
    if d < 1:
        brake_torque = 5
        motor_torque = 5
    else:
        brake_torque = 10
        motor_torque = 10
    if distance < 0:
        motor_torque *= -1
    return WheelValues(brake_at=brake_at, brake_torque=brake_torque, left_motor_torque=motor_torque,
                       right_motor_torque=motor_torque, steer_angle=0)
