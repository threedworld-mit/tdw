import numpy as np


class Bound:
    def __init__(self, front: np.array, back: np.array, left: np.array, right: np.array, top: np.array,
                 bottom: np.array, center: np.array):
        self.front: np.array = front
        self.back: np.array = back
        self.left: np.array = left
        self.right: np.array = right
        self.top: np.array = top
        self.bottom: np.array = bottom
        self.center: np.array = center
