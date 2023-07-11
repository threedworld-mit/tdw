import numpy as np


class VRayMatrix:
    """
    Matrix data for a VRay object or camera.
    """

    """:class_var
    Conversion matrix from Y-up to Z-up, and left-hand to right-hand.
    """
    HANDEDNESS: np.ndarray = np.array([[-1, 0, 0, 0],
                                       [0, 0, -1, 0],
                                       [0, -1, 0, 0],
                                       [0, 0, 0, 1]])

    def __init__(self, column_one: str, column_two: str, column_three: str, column_four: str):
        self.column_one: str = column_one
        self.column_two: str = column_two
        self.column_three: str = column_three
        self.column_four: str = column_four


def get_converted_node_matrix(matrix: np.ndarray) -> VRayMatrix:
    """
    :param matrix: The object transform matrix.

    :return: The converted matrix as a `VRayMatrix`.
    """

    # Equivalent to: handedness * object_matrix * handedness.
    m = np.matmul(np.matmul(VRayMatrix.HANDEDNESS, matrix), VRayMatrix.HANDEDNESS)
    # V-Ray units are in centimeters while Unity's are in meters, so we need to multiply the position values by 100.
    pos_x = (m[3][0] * 100)
    pos_y = (m[3][1] * 100)
    pos_z = -(m[3][2] * 100)
    return VRayMatrix(column_one='{:f}'.format(m[0][0]) + "," + '{:f}'.format(m[0][1]) + "," + '{:f}'.format(-m[0][2]),
                      column_two='{:f}'.format(m[1][0]) + "," + '{:f}'.format(m[1][1]) + "," + '{:f}'.format(-m[1][2]),
                      column_three='{:f}'.format(-m[2][0]) + "," + '{:f}'.format(-m[2][1]) + "," + '{:f}'.format(m[2][2]),
                      column_four='{:f}'.format(pos_x) + "," + '{:f}'.format(pos_y) + "," + '{:f}'.format(pos_z))


def get_converted_camera_matrix(avatar_matrix: np.ndarray, sensor_matrix: np.ndarray) -> VRayMatrix:
    """
    :param avatar_matrix: The avatar transform matrix.
    :param sensor_matrix: The sensor container matrix.

    :return: The converted matrices as a `VRayMatrix`.
    """

    # Equivalent to: handedness * object_matrix * handedness.
    pos_matrix = np.matmul(np.matmul(VRayMatrix.HANDEDNESS, avatar_matrix), VRayMatrix.HANDEDNESS)
    rot_matrix = np.matmul(np.matmul(VRayMatrix.HANDEDNESS, sensor_matrix), VRayMatrix.HANDEDNESS)
    # V-Ray units are in centimeters while Unity's are in meters, so we need to multiply the position values by 100.
    # We also need to negate the Z value, to complete the handedness conversion.
    pos_x = (pos_matrix[3][0] * 100)
    pos_y = (pos_matrix[3][1] * 100)
    pos_z = -(pos_matrix[3][2] * 100)
    return VRayMatrix(column_one='{:f}'.format(-rot_matrix[0][0]) + "," + '{:f}'.format(-rot_matrix[0][1]) + "," + '{:f}'.format(rot_matrix[0][2]),
                      column_two='{:f}'.format(-rot_matrix[2][0]) + "," + '{:f}'.format(-rot_matrix[2][1]) + "," + '{:f}'.format(rot_matrix[2][2]),
                      column_three='{:f}'.format(rot_matrix[1][0]) + "," + '{:f}'.format(rot_matrix[1][1]) + "," + '{:f}'.format(-rot_matrix[1][2]),
                      column_four='{:f}'.format(pos_x) + "," + '{:f}'.format(pos_y) + "," + '{:f}'.format(pos_z))
