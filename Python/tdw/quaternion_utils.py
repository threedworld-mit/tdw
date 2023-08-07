import numpy as np


class QuaternionUtils:
    """
    Helper functions for using quaternions.

    Quaternions are always numpy arrays in the following order: `[x, y, z, w]`.

    This is the same order as any quaternion found in TDW's output data, e.g. `Transforms.get_rotation(index)`.

    Vectors are always numpy arrays in the following order: `[x, y, z]`.
    """

    """:class_var
    The global up directional vector.
    """
    UP: np.ndarray = np.array([0, 1, 0])
    """:class_var
    The global forward directional vector.
    """
    FORWARD: np.ndarray = np.array([0, 0, 1])
    """:class_var
    The global right directional vector.
    """
    RIGHT: np.ndarray = np.array([1, 0, 0])
    """:class_var
    The quaternion identity rotation.
    """
    IDENTITY: np.ndarray = np.array([0, 0, 0, 1])
    _POLE: float = 0.49995

    @staticmethod
    def get_inverse(q: np.ndarray) -> np.ndarray:
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

        return np.array([-x, -y, -z, w]) * inv

    @staticmethod
    def multiply(q1: np.ndarray, q2: np.ndarray) -> np.ndarray:
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
    def get_conjugate(q: np.ndarray) -> np.ndarray:
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
    def multiply_by_vector(q: np.ndarray, v: np.ndarray) -> np.ndarray:
        """
        Multiply a quaternion by a vector.

        Source: https://stackoverflow.com/questions/4870393/rotating-coordinate-system-via-a-quaternion

        :param q: The quaternion.
        :param v: The vector.

        :return: A directional vector calculated from: `q * v`
        """

        q2 = np.array([v[0], v[1], v[2], 0.0])
        return QuaternionUtils.multiply(QuaternionUtils.multiply(q, q2), QuaternionUtils.get_conjugate(q))[:-1]

    @staticmethod
    def world_to_local_vector(position: np.ndarray, origin: np.ndarray, rotation: np.ndarray) -> np.ndarray:
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
    def get_up_direction(q: np.ndarray) -> np.ndarray:
        """
        :param q: The rotation as a quaternion.

        :return: A directional vector corresponding to the "up" direction from the quaternion.
        """

        return QuaternionUtils.multiply_by_vector(q, QuaternionUtils.UP)

    @staticmethod
    def euler_angles_to_quaternion(euler: np.ndarray) -> np.ndarray:
        """
        Convert Euler angles to a quaternion.

        Source: https://pastebin.com/riRLRvch

        :param euler: The Euler angles vector.

        :return: The quaternion representation of the Euler angles.
        """

        pitch = np.radians(euler[0] * 0.5)
        cp = np.cos(pitch)
        sp = np.sin(pitch)

        yaw = np.radians(euler[1] * 0.5)
        cy = np.cos(yaw)
        sy = np.sin(yaw)

        roll = np.radians(euler[2] * 0.5)
        cr = np.cos(roll)
        sr = np.sin(roll)

        x = sy * cp * sr + cy * sp * cr
        y = sy * cp * cr - cy * sp * sr
        z = cy * cp * sr - sy * sp * cr
        w = cy * cp * cr + sy * sp * sr
        return np.abs(np.array([x, y, z, w]))

    @staticmethod
    def quaternion_to_euler_angles(quaternion: np.ndarray) -> np.ndarray:
        """
        Convert a quaternion to Euler angles.

        Source: https://stackoverflow.com/a/12122899

        :param quaternion: A quaternion as a nump array.

        :return: The Euler angles representation of the quaternion.
        """

        x = quaternion[0]
        y = quaternion[1]
        z = quaternion[2]
        w = quaternion[3]

        sqx = x * x
        sqy = y * y
        sqz = z * z
        sqw = w * w

        unit = sqx + sqy + sqz + sqw
        test = x * w - y * z

        if test > QuaternionUtils._POLE * unit:
            ex = np.pi / 2
            ey = 2 * np.arctan2(y, x)
            ez = 0
        elif test < -QuaternionUtils._POLE * unit:
            ex = -np.pi / 2
            ey = -2 * np.arctan2(y, x)
            ez = 0
        else:
            qx = w
            qy = z
            qz = x
            qw = y
            sqqz = qz * qz
            ex = np.arcsin(2 * (qx * qz - qw * qy))
            ey = np.arctan2(2 * qx * qw + 2 * qy * qz, 1 - 2 * (sqqz + qw * qw))
            ez = np.arctan2(2 * qx * qy + 2 * qz * qw, 1 - 2 * (qy * qy + sqqz))
        return np.degrees(np.array([ex, ey, ez])) % 360

    @staticmethod
    def get_y_angle(q1: np.ndarray, q2: np.ndarray) -> float:
        """
        Source: https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles

        :param q1: The first quaternion.
        :param q2: The second quaternion.

        :return: The angle between the two quaternions in degrees around the y axis.
        """

        qd = QuaternionUtils.multiply(QuaternionUtils.get_conjugate(q1), q2)
        return np.rad2deg(2 * np.arcsin(np.clip(qd[1], -1, 1)))

    @staticmethod
    def is_left_of(origin: np.ndarray, target: np.ndarray, forward: np.ndarray) -> bool:
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
        perpendicular: np.ndarray = np.cross(forward, target_direction)
        direction = np.dot(perpendicular, QuaternionUtils.UP)
        return direction > 0
