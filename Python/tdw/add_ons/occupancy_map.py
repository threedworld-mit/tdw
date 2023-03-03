from typing import List, Optional
import numpy as np
from tdw.output_data import OutputData
from tdw.output_data import OccupancyMap as Occ
from tdw.add_ons.add_on import AddOn


class OccupancyMap(AddOn):
    """
    An occupancy map is a numpy array that divides a TDW into a grid. Each cell is free (no objects), non-free (has objects), or is outside of the environment.

    Each element in the occupancy map can be one of three values:

    | Value | Meaning                                                      |
    | ----- | ------------------------------------------------------------ |
    | 0     | The cell is unoccupied.                                      |
    | 1     | The cell is occupied by at least one object or occupied by an environment object (such as a wall). |
    | 2    | The cell is out of bounds (there is no floor).               |
    | 3    | The cell is free, but it's in an isolated island. |
    """

    def __init__(self):
        """
        (no parameters)
        """

        super().__init__()
        """:field
        A 2D numpy array of the occupancy map. Each value is an occupancy value. For example, if `self.occupancy_map[0][1] == 0`, then that position is free. This array is `None` until you call `generate()` followed by `controller.communicate(commands)`.
        """
        self.occupancy_map: Optional[np.ndarray] = None
        """:field
        A 3D numpy array of the occupancy map worldspace positions where the shape is `(width, length, 2)` where the last axis is (x, z) worldspace coordinates. The lengths of the first two axes of this array are the same as in `self.occupancy_map`, meaning that `self.occupancy_map[0][1]` is the occupancy status of `self.positions[0][1]`. This array is `None` until you call `generate()` followed by `controller.communicate(commands)`. 
        """
        self.positions: Optional[np.ndarray] = None
        self._cell_size: float = 0
        self.initialized = True

    def get_initialization_commands(self) -> List[dict]:
        return []

    def on_send(self, resp: List[bytes]) -> None:
        # Update the occupancy map.
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "occu":
                occupancy_map = Occ(resp[i])
                self.occupancy_map = occupancy_map.get_map()
                self.positions = occupancy_map.get_positions()

    def generate(self, ignore_objects: List[int] = None, cell_size: float = 0.5, raycast_y: float = 2.7, once: bool = True) -> None:
        """
        Generate an occupancy map. Call this, followed by `controller.communicate(commands)` to generate the map.

        :param ignore_objects: If not None, ignore these objects when determining if a cell is free or non-free.
        :param cell_size: The cell size in meters.
        :param raycast_y: Raycast for objects from this height in meters.
        :param once: If True, generate an occupancy map only on this `communicate(commands)` call. If False, regenerate the occupancy map on every `communicate(commands)` call using the parameters provided here until the scene is unloaded or this function is called again.
        """

        self._cell_size = cell_size
        self.commands.append({"$type": "send_occupancy_map",
                              "cell_size": cell_size,
                              "ignore_objects": [] if ignore_objects is None else ignore_objects,
                              "raycast_y": raycast_y,
                              "frequency": "once" if once else "always"})

    def show(self) -> None:
        """
        Visualize the occupancy map by adding blue squares into the scene to mark free spaces.

        These blue squares don't interact with the physics engine.
        """

        if self.occupancy_map is None:
            raise Exception("The occupancy map hasn't been generated and initialized (see documentation).")
        for ix, iz in np.ndindex(self.occupancy_map.shape):
            if self.occupancy_map[ix][iz] != 0:
                continue
            p = self.positions[ix][iz]
            self.commands.append({"$type": "add_position_marker",
                                  "position": {"x": float(p[0]), "y": 0.05, "z": float(p[1])},
                                  "scale": self._cell_size * 0.9,
                                  "color": {"r": 0, "g": 0, "b": 1, "a": 1},
                                  "shape": "square"})

    def hide(self) -> None:
        """
        Remove all positions markers (the blue squares created by `self.show()`).
        """

        self.commands.append({"$type": "remove_position_markers"})
