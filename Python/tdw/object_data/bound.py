import numpy as np


class Bound:
    """
    Bounds data for a single object.
    """

    def __init__(self, front: np.ndarray, back: np.ndarray, left: np.ndarray, right: np.ndarray, top: np.ndarray,
                 bottom: np.ndarray, center: np.ndarray):
        """
        :param front: The position of the front point.
        :param back: The position of the back point.
        :param left: The position of the left point.
        :param right: The position of the right point.
        :param top: The position of the top point.
        :param bottom: The position of the bottom point.
        :param center: The position of the center point.
        """

        """:field
        The position of the front point.
        """
        self.front: np.ndarray = front
        """:field
        The position of the back point.
        """
        self.back: np.ndarray = back
        """:field
        The position of the left point.
        """
        self.left: np.ndarray = left
        """:field
        The position of the right point.
        """
        self.right: np.ndarray = right
        """:field
        The position of the top point.
        """
        self.top: np.ndarray = top
        """:field
        The position of the bottom point.
        """
        self.bottom: np.ndarray = bottom
        """:field
        The position of the center point.
        """
        self.center: np.ndarray = center
