import numpy as np
from tdw.output_data import StaticRobot


class NonMoving:
    """
    Static data for a non-moving object attached to a robot (i.e. a sub-object mesh of a limb).
    """

    def __init__(self, static_robot: StaticRobot, index: int):
        """
        :param static_robot: Static robot output data from the build.
        :param index: The index of this object in the list of non-moving objects.
        """

        """:field
        The ID of this object.
        """
        self.object_id: int = static_robot.get_non_moving_id(index)
        """:field
        The name of this object.
        """
        self.name: str = static_robot.get_non_moving_name(index)
        """:field
        The segmentation color of this joint as an `[r, g, b]` numpy array.
        """
        self.segmentation_color: np.ndarray = np.array(static_robot.get_non_moving_segmentation_color(index))
