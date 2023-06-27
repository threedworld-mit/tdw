from typing import Tuple


def get_turn_values(angle: float) -> Tuple[float, float, float, float, float]:
    """
    :param angle: The target angle in degrees.

    :return: Wheel parameters: `brake_at, brake_torque, left_motor_torque, right_motor_torque, steer_angle`.
    """

    brake_at = angle * 0.9
    a = abs(angle)
    if a < 5:
        brake_torque = 2.5
        outer_motor_torque = -2.5
        inner_motor_torque = 5
        steer_angle = 25
    else:
        brake_torque = 5
        outer_motor_torque = -5
        inner_motor_torque = 10
        steer_angle = 45
    if angle > 0:
        left_motor_torque = outer_motor_torque
        right_motor_torque = inner_motor_torque
    else:
        left_motor_torque = inner_motor_torque
        right_motor_torque = outer_motor_torque
        brake_torque *= -1
        steer_angle *= -1
    return brake_at, brake_torque, left_motor_torque, right_motor_torque, steer_angle
