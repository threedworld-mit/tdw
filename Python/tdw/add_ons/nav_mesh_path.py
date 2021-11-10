import numpy as np
from typing import List, Dict, Union
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.add_on import AddOn
from tdw.output_data import OutputData
from tdw.output_data import NavMeshPath as Path


class NavMeshPath:
    """
    Lightweight wrapper class for `NavMeshPath` output data.
    """

    def __init__(self, path: Path):
        """
        :param path: The `NavMeshPath` output data. Type `Path` in this case is a name alias for `NavMeshPath`.
        """

        """:field
        The ID of the path.
        """
        self.path_id: int = path.get_id()
        """:field
        The state of the path.
        """
        self.path_state: str = path.get_state()
        """:field
        A list of of Vector3 dictionary positions in the path.
        """
        self.path: List[Dict[str, float]] = list()
        for point in path.get_path():
            self.path.append(TDWUtils.array_to_vector3(point))
        """:field
        An index in `self.path` for the current position\.
        """
        self.index = 0
