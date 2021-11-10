import numpy as np
from typing import List, Dict, Union
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.add_on import AddOn
from tdw.output_data import OutputData, StaticRigidbodies
from tdw.output_data import NavMeshPath as Path
from tdw.nav_mesh_data.nav_mesh_path import NavMeshPath


class NavMesh(AddOn):
    """
    Generate NavMeshes and return paths along the NavMesh.
    """

    def __init__(self, bake: bool = False):
        """
        :param bake: If True, bake the NavMesh. Set this to True only when using the proc-gen room.
        """

        super().__init__()
        self._bake: bool = bake
        self._initialized_nav_mesh: bool = False
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

    def reset(self, bake: bool = False) -> None:
        """
        Call this when the scene resets to reinitialize this add-on. `self.paths` will be cleared.

        :param bake: If True, bake the NavMesh. Set this to True only when using the proc-gen room.
        """

        self.initialized = False
        self._initialized_nav_mesh = False
        self._bake = bake

    def get_initialization_commands(self) -> List[dict]:
        self.paths.clear()
        self._initialized_nav_mesh = False
        return [{"$type": "send_static_rigidbodies"}]

    def on_send(self, resp: List[bytes]) -> None:
        if not self._initialized_nav_mesh:
            self._initialized_nav_mesh = True
            carver_ids: List[int] = list()
            nav_mesh_obstacle_commands: List[dict] = list()
            # Get static Rigidbody data.
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                if r_id == "srig":
                    srig = StaticRigidbodies(resp[i])
                    for j in range(srig.get_num()):
                        carver_id = srig.get_id(j)
                        carver_ids.append(carver_id)
                        nav_mesh_obstacle_commands.append({"$type": "make_nav_mesh_obstacle",
                                                           "id": carver_id,
                                                           "carve_type": "stationary" if srig.get_kinematic(j) else "all"})
            # Bake a new NavMesh.
            if self._bake:
                self.commands.append({"$type": "bake_nav_mesh",
                                      "carve_type": "all",
                                      "ignore": carver_ids})
            # Set carvers.
            self.commands.extend(nav_mesh_obstacle_commands)
        else:
            # Update path data.
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                if r_id == "path":
                    p = NavMeshPath(Path(resp[i]))
                    self.paths[p.path_id] = p
