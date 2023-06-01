import numpy as np


class JointDynamic:
    """
    Dynamic info for a joint that can change per-frame, such as its current position.
    """

    def __init__(self, joint_id: int, position: np.ndarray, angles: np.ndarray, moving: bool):
        """
        :param joint_id: The ID of this joint.
        :param position: The worldspace position of this joint as an `[x, y, z]` numpy array.
        :param angles: The angles of each axis of the joint in degrees as a numpy array. For prismatic joints, you need to convert this from degrees to radians in order to get the correct distance in meters.
        :param moving: If True, this joint is currently moving.
        """

        """:field
        The ID of this joint.
        """
        self.joint_id: int = joint_id
        """:field
        The worldspace position of this joint as an `[x, y, z]` numpy array.
        """
        self.position: np.ndarray = position
        """:field
        The angles of each axis of the joint in degrees. For prismatic joints, you need to convert this from degrees to radians in order to get the correct distance in meters.
        """
        self.angles: np.ndarray = angles
        """:field
        If True, this joint is currently moving.
        """
        self.moving: bool = moving
