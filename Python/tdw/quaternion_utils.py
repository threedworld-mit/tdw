import numpy as np


class QuaternionUtils:
    """
    Helper functions for using quaternions.

    Quaternions are always numpy arrays in the following order: `[x, y, z, w]`.
    This is the order returned in all Output Data objects.

    Vectors are always numpy arrays in the following order: `[x, y, z]`.
    """

    """:class_var
    The global up directional vector.
    """
    UP = np.array([0, 1, 0])
    """:class_var
    The global forward directional vector.
    """
    FORWARD: np.array = np.array([0, 0, 1])
    """:class_var
    The quaternion identity rotation.
    """
    IDENTITY = np.array([0, 0, 0, 1])

    @staticmethod
    def get_inverse(q: np.array) -> np.array:
        """
        Source: https://referencesource.microsoft.com/#System.Numerics/System/Numerics/Quaternion.cs

        :param q: The quaternion.

        :return: The inverse of the quaternion.
        """

        x = q[0]
        y = q[1]
        z = q[2]
        w = q[3]

        ls = x * x + y * y + z * z + w * w
        inv = 1.0 / ls

        return np.array([-x * inv, -y * inv, -z * inv, w * inv])

    @staticmethod
    def multiply(q1: np.array, q2: np.array) -> np.array:
        """
        Multiply two quaternions.
        Source: https://stackoverflow.com/questions/4870393/rotating-coordinate-system-via-a-quaternion

        :param q1: The first quaternion.
        :param q2: The second quaternion.
        :return: The multiplied quaternion: `q1 * q2`
        """

        x1 = q1[0]
        y1 = q1[1]
        z1 = q1[2]
        w1 = q1[3]

        x2 = q2[0]
        y2 = q2[1]
        z2 = q2[2]
        w2 = q2[3]

        w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
        x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
        y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
        z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
        return np.array([x, y, z, w])

    @staticmethod
    def get_conjugate(q: np.array) -> np.array:
        """
        Source: https://stackoverflow.com/questions/4870393/rotating-coordinate-system-via-a-quaternion

        :param q: The quaternion.

        :return: The conjugate of the quaternion: `[-x, -y, -z, w]`
        """

        x = q[0]
        y = q[1]
        z = q[2]
        w = q[3]

        return np.array([-x, -y, -z, w])

    @staticmethod
    def multiply_by_vector(q: np.array, v: np.array) -> np.array:
        """
        Multiply a quaternion by a vector.
        Source: https://stackoverflow.com/questions/4870393/rotating-coordinate-system-via-a-quaternion

        :param q: The quaternion.
        :param v: The vector.

        :return: A directional vector calculated from: `q * v`
        """

        q2 = (v[0], v[1], v[2], 0.0)
        return QuaternionUtils.multiply(QuaternionUtils.multiply(q, q2), QuaternionUtils.get_conjugate(q))[:-1]

    @staticmethod
    def world_to_local_vector(position: np.array, origin: np.array, rotation: np.array) -> np.array:
        """
        Convert a vector position in absolute world coordinates to relative local coordinates.
        Source: https://answers.unity.com/questions/601062/what-inversetransformpoint-does-need-explanation-p.html

        :param position: The position vector in world coordinates.
        :param origin: The origin vector of the local space in world coordinates.
        :param rotation: The rotation quaternion of the local coordinate space.

        :return: `position` in local coordinates.
        """

        return QuaternionUtils.multiply_by_vector(q=QuaternionUtils.get_inverse(q=rotation), v=position - origin)

    @staticmethod
    def get_up_direction(q: np.array) -> np.array:
        """
        :param q: The rotation as a quaternion.

        :return: A directional vector corresponding to the "up" direction from the quaternion.
        """

        return QuaternionUtils.multiply_by_vector(q, QuaternionUtils.UP)

    @staticmethod
    def euler_angles_to_quaternion(euler: np.array) -> np.array:
        """
        Convert Euler angles to a quaternion.

        :param euler: The Euler angles vector.

        :return: The quaternion representation of the Euler angles.
        """

        roll = euler[0]
        pitch = euler[1]
        yaw = euler[2]
        cy = np.cos(yaw * 0.5)
        sy = np.sin(yaw * 0.5)
        cp = np.cos(pitch * 0.5)
        sp = np.sin(pitch * 0.5)
        cr = np.cos(roll * 0.5)
        sr = np.sin(roll * 0.5)

        w = cy * cp * cr + sy * sp * sr
        x = cy * cp * sr - sy * sp * cr
        y = sy * cp * sr + cy * sp * cr
        z = sy * cp * cr - cy * sp * sr
        return np.array([x, y, z, w])

    @staticmethod
    def quaternion_to_euler_angles(quaternion: np.array) -> np.array:
        """
        Convert a quaternion to Euler angles.

        :param quaternion: A quaternion as a nump array.

        :return: The Euler angles representation of the quaternion.
        """

        x = quaternion[0]
        y = quaternion[1]
        z = quaternion[2]
        w = quaternion[3]
        ysqr = y * y

        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + ysqr)
        ex = np.degrees(np.arctan2(t0, t1))

        t2 = +2.0 * (w * y - z * x)
        t2 = np.where(t2 > +1.0, +1.0, t2)

        t2 = np.where(t2 < -1.0, -1.0, t2)
        ey = np.degrees(np.arcsin(t2))

        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (ysqr + z * z)
        ez = np.degrees(np.arctan2(t3, t4))

        return np.array([ex, ey, ez])

    @staticmethod
    def get_y_angle(q1: np.array, q2: np.array) -> float:
        """
        Source: https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles

        :param q1: The first quaternion.
        :param q2: The second quaternion.

        :return: The angle between the two quaternions in degrees around the y axis.
        """

        qd = QuaternionUtils.multiply(QuaternionUtils.get_conjugate(q1), q2)
        return np.rad2deg(2 * np.arcsin(np.clip(qd[1], -1, 1)))

    @staticmethod
    def is_left_of(origin: np.array, target: np.array, forward: np.array) -> bool:
        """
        :param origin: The origin position.
        :param target: The target position.
        :param forward: The forward directional vector.

        :return: True if `target` is to the left of `origin` by the `forward` vector; False if it's to the right.
        """

        # Get the heading.
        target_direction = target - origin
        # Normalize the heading.
        target_direction = target_direction / np.linalg.norm(target_direction)
        perpendicular: np.array = np.cross(forward, target_direction)
        direction = np.dot(perpendicular, QuaternionUtils.UP)
        return direction > 0
