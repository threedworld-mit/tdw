from typing import List, Union, Dict
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Transforms
import numpy as np

class ReplicantUtils():

    @staticmethod
    def get_object_position(resp: List[bytes], object_id: int):
        for i in range(len(resp) - 1):
            # Get the output data ID.
            r_id = OutputData.get_data_type_id(resp[i])
            # This is transforms output data.
            if r_id == "tran":
                transforms = Transforms(resp[i])
                for j in range(transforms.get_num()):
                    if transforms.get_id(j) == object_id:
                        return TDWUtils.array_to_vector3(transforms.get_position(j))


    
    @staticmethod
    def get_direction(self, forward: np.array, origin: np.array, target: np.array) -> bool:
        """
        :param forward: The forward directional vector.
        :param origin: The origin position.
        :param target: The target position.

        :return: True if the target is to the left of the origin by the forward vector; False if it's to the right.
        """
        # Get the heading.
        target_direction = target - origin
        # Normalize the heading.
        #target_direction = target_direction / np.linalg.norm(target_direction)
        perpendicular: np.array = np.cross(forward, target_direction)
        direction = np.dot(perpendicular, QuaternionUtils.UP)
        return direction

