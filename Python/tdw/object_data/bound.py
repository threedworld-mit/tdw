import numpy as np


class Bound:
    """
    Bounds data for a single object.
    """

    def __init__(self, front: np.array, back: np.array, left: np.array, right: np.array, top: np.array,
                 bottom: np.array, center: np.array):
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
        self.front: np.array = front
        """:field
        The position of the back point.
        """
        self.back: np.array = back
        """:field
        The position of the left point.
        """
        self.left: np.array = left
        """:field
        The position of the right point.
        """
        self.right: np.array = right
        """:field
        The position of the top point.
        """
        self.top: np.array = top
        """:field
        The position of the bottom point.
        """
        self.bottom: np.array = bottom
        """:field
        The position of the center point.
        """
        self.center: np.array = center
