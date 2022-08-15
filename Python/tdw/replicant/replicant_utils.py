from typing import List, Union, Dict
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Transforms
import numpy as np

class ReplicantUtils():

    @staticmethod
    def get_object_position(resp: List[bytes], object_id: int):
        print(str(resp))
        for i in range(len(resp) - 1):
            # Get the output data ID.
            r_id = OutputData.get_data_type_id(resp[i])
            # This is transforms output data.
            if r_id == "tran":
                transforms = Transforms(resp[i])
                for j in range(transforms.get_num()):
                    if transforms.get_id(j) == object_id:
                        return TDWUtils.array_to_vector3(transforms.get_position(j))



    