import numpy as np
from typing import List, Dict, Union
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.add_on import AddOn
from tdw.output_data import OutputData
from tdw.output_data import NavMeshPath as Path
from tdw.add_ons.nav_mesh_path import NavMeshPath


class NavMesh(AddOn):
    """
    Generate NavMeshes and return paths along the NavMesh.
    """
    
    def __init__(self, carver_ids: Dict[int, bool], bake: bool = False):
        """
        :param carver_ids: A dictionary of object IDs for objects that will carve holes into the NavMesh. Value = Boolean; if True, this is a "stationary" object (usually a kinematic object) and will carve a relatively large hole.
        :param bake: If True, bake the NavMesh. Set this to True only when using the proc-gen room.
        """

        super().__init__()
        self._carver_ids: Dict[int, bool] = carver_ids
        self._bake: bool = bake
        """:field
        A dictionary of paths. This is updated by calling `self.get_path(origin, destination, path_id)` followed by `c.communicate(commands)`. Key = path ID. Value = [`NavMeshPath`](nav_mesh_path.md). This is reset when `self.reset()` is called.
        """
        self.paths: Dict[int, NavMeshPath] = dict()

    def get_path(self, origin: Union[np.ndarray, Dict[str, float]], destination: Union[np.ndarray, Dict[str, float]],
                 path_id: int = 0) -> None:
        """
        Request a new path. The new path will be returned in the next `c.communicate(commands)` call; see `self.paths`.

        :param origin: The origin position as a numpy array or Vector3 dictionary.
        :param destination: The destination position as a numpy array or Vector3 dictionary.
        :param path_id: The ID of this path.
        """

        if isinstance(origin, np.ndarray):
            o = TDWUtils.array_to_vector3(origin)
        else:
            o = origin
        if isinstance(destination, np.ndarray):
            d = TDWUtils.array_to_vector3(destination)
        else:
            d = destination
        self.commands.append({"$type": "send_nav_mesh_path",
                              "origin": o,
                              "destination": d,
                              "id": path_id})

    def reset(self, carver_ids: Dict[int, bool] = None, bake: bool = False) -> None:
        """
        Call this when the scene resets to reinitialize this add-on. `self.paths` will be cleared.

        :param carver_ids: If not None, this is the dictionary of the new scene's carver IDs (see constructor documentation).
        :param bake: If True, bake the NavMesh. Set this to True only when using the proc-gen room.
        """

        self.initialized = False
        if carver_ids is not None:
            self._carver_ids = carver_ids
        else:
            self._carver_ids.clear()
        self._bake = bake

    def get_initialization_commands(self) -> List[dict]:
        self.paths.clear()
        commands = []
        # Bake the NavMesh. Ignore objects so that we can specify them individually.
        if self._bake:
            commands.append({"$type": "bake_nav_mesh",
                             "carve_type": "all",
                             "ignore": [list(self._carver_ids.keys())]})
        # Set carvers based on kinematic state.
        for object_id in self._carver_ids:
            commands.append({"$type": "make_nav_mesh_obstacle",
                             "id": object_id,
                             "carve_type": "stationary" if self._carver_ids[object_id] else "all"})
        return commands

    def on_send(self, resp: List[bytes]) -> None:
        # Update path data.
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "path":
                p = NavMeshPath(Path(resp[i]))
                self.paths[p.path_id] = p
