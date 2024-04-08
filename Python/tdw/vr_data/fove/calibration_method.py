from enum import Enum


class CalibrationMethod(Enum):
    """
    Indicate the calibration method to use.
    """

    default = 0
    one_point = 1  #requires license
    spiral = 2
    one_point_with_no_glasses_spiral_with_glasses = 3
    zero_point = 4  #requires license
    default_calibration = 5

