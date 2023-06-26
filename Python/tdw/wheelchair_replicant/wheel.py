class Wheel:
    """
    A wheelchair wheel.
    """

    def __init__(self, motor_torque: float, brake_torque: float, steer_angle: float):
        """
        :param motor_torque: The motor torque.
        :param brake_torque: The brake torque.
        :param steer_angle: The steer angle in degrees.
        """

        """:field
        The motor torque.
        """
        self.motor_torque: float = motor_torque
        """:field
         The brake torque.
        """
        self.brake_torque: float = brake_torque
        """:field
        The steer angle in degrees.
        """
        self.steer_angle: float = steer_angle
