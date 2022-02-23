from typing import List, Dict, Optional, Tuple
import numpy as np
from tdw.output_data import OutputData, Raycast, Overlap
from tdw.add_ons.add_on import AddOn
from tdw.scene_data.scene_bounds import SceneBounds


class OccupancyMap(AddOn):
    """
    An occupancy map is a numpy array that divides a TDW into a grid. Each cell is free (no objects), non-free (has objects), or is outside of the environment.

    Each element in the occupancy map can be one of three values:

    | Value | Meaning                                                      |
    | ----- | ------------------------------------------------------------ |
    | -1    | The cell is out of bounds (there is no floor).               |
    | 1     | The cell is occupied by at least one object, occupied by an environment object (such as a wall), or otherwise not navigable (blocked by other objects). |
    | 0     | The cell is unoccupied.                                      |
    """

    # The height from which rays will be cast.
    _RAYCAST_Y: float = 100

    def __init__(self, cell_size: float = 0.5):
        """
        :param cell_size: The diameter of each cell in meters.
        """

        super().__init__()
        """:field
        A 2-dimensional numpy array of the occupancy map. Each row corresponds to a worldspace x value and each column corresponds to a worldspace z value (see `get_occupancy_position(idx, idy)` below).
        """
        self.occupancy_map: Optional[np.array] = None
        """:field
        The [bounds of the scene](../scene_data/scene_bounds.md).
        """
        self.scene_bounds: Optional[SceneBounds] = None
        # The diameter of each cell in meters.
        self._cell_size: float = cell_size
        # The expected dimensions of the occupancy map array.
        self._occupancy_map_size: Tuple[int, int] = (0, 0)
        # Ignore these objects when generating the occupancy map.
        self._ignore_objects: List[int] = list()

    def get_initialization_commands(self) -> List[dict]:
        return [{"$type": "send_scene_regions"}]

    def on_send(self, resp: List[bytes]) -> None:
        def __get_islands() -> List[List[Tuple[int, int]]]:
            """
            :return: A list of all islands, i.e. continuous zones of traversability on the occupancy map.
            """

            # Positions that have been reviewed so far.
            traversed: List[Tuple[int, int]] = []
            islands: List[List[Tuple[int, int]]] = list()

            for ox, oy in np.ndindex(self.occupancy_map.shape):
                op = (ox, oy)
                if op in traversed:
                    continue
                # Fill the island (a continuous zone) that position `p` belongs to.
                to_check: List[tuple] = [op]
                island: List[Tuple[int, int]] = list()
                while len(to_check) > 0:
                    # Check the next position.
                    op = to_check.pop(0)
                    if op[0] < 0 or op[0] >= self.occupancy_map.shape[0] or op[1] < 0 or \
                            op[1] >= self.occupancy_map.shape[1] or \
                            self.occupancy_map[op[0]][op[1]] != 0 or op in island:
                        continue
                    # Mark the position as traversed.
                    island.append(op)
                    # Check these neighbors.
                    px, py = op
                    to_check.extend([(px, py + 1),
                                     (px + 1, py + 1),
                                     (px + 1, py),
                                     (px + 1, py - 1),
                                     (px, py - 1),
                                     (px - 1, py - 1),
                                     (px - 1, py),
                                     (px - 1, py + 1)])
                if len(island) > 0:
                    for island_position in island:
                        traversed.append(island_position)
                    islands.append(island)
            return islands

        # Set the scene bounds.
        if self.scene_bounds is None:
            self.scene_bounds = SceneBounds(resp=resp)
        if self.occupancy_map is None:
            # Generate the occupancy map.
            self.occupancy_map = np.zeros(shape=(self._occupancy_map_size[0] + 1, self._occupancy_map_size[1] + 1),
                                          dtype=int)
            # Get all of the positions that are actually in the environment.
            hit_env: Dict[int, bool] = dict()
            # Get all of the overlaps to determine if there was an object.
            hit_obj: Dict[int, bool] = dict()
            # The IDs of each object in the overlap.
            hit_obj_ids: Dict[int, np.array] = dict()
            hit_walls: Dict[int, bool] = dict()
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                if r_id == "rayc":
                    raycast = Raycast(resp[i])
                    hit_env[raycast.get_raycast_id()] = raycast.get_hit()
                elif r_id == "over":
                    overlap = Overlap(resp[i])
                    overlap_id = overlap.get_id()
                    hit_obj[overlap_id] = len(overlap.get_object_ids()) > 0
                    hit_obj_ids[overlap_id] = overlap.get_object_ids()
                    hit_walls[overlap_id] = overlap.get_walls()

            for cast_id in hit_env:
                idx = cast_id % 10000
                idz = int((cast_id - (cast_id % 10000)) / 10000)
                # The position is outside of the environment.
                if not hit_env[cast_id]:
                    self.occupancy_map[idx][idz] = -1
                # The position is occupied by at least one object that we aren't ignoring.
                elif hit_walls[cast_id] or (hit_obj[cast_id] and len([o for o in hit_obj_ids[cast_id] if o not in self._ignore_objects]) > 0):
                    self.occupancy_map[idx][idz] = 1
                # The position is free.
                else:
                    self.occupancy_map[idx][idz] = 0
            # Assume that the edges of the occupancy map are out of bounds.
            for ix, iy in np.ndindex(self.occupancy_map.shape):
                if ix == 0 or ix == self.occupancy_map.shape[0] - 1 or iy == 0 or \
                        iy == self.occupancy_map.shape[1] - 1:
                    self.occupancy_map[ix][iy] = -1
            # Sort the free positions of the occupancy map into continuous "islands".
            # Then, sort that list of lists by length.
            # The longest list is the biggest "island" i.e. the navigable area.
            non_navigable = list(sorted(__get_islands(), key=len))[:-1]
            # Record non-navigable positions.
            for n in non_navigable:
                for p in n:
                    self.occupancy_map[p[0]][p[1]] = -1

    def generate(self, ignore_objects: List[int] = None) -> None:
        """
        Generate an occupancy map.
        This function should only be called at least one controller.communicate() call after adding this add-on.
        The OccupancyMap then requires one more controller.communicate() call to create the occupancy map.
        (See the example at the top of this document.)

        :param ignore_objects: If not None, ignore these objects when determining if a cell is free or non-free.
        """

        if not self.initialized:
            raise Exception("Can't generate an occupancy map because this add-on hasn't initialized.\n"
                            "Wait at least one controller.communicate() call before calling occupancy_map.generate()")
        self.occupancy_map = None
        if ignore_objects is None:
            self._ignore_objects.clear()
        else:
            self._ignore_objects = ignore_objects
        # Spherecast to each point.
        x = self.scene_bounds.x_min
        idx = 0
        idz = 0
        capsule_half_height = (self.scene_bounds.y_max - self.scene_bounds.y_min) / 2
        while x < self.scene_bounds.x_max:
            z = self.scene_bounds.z_min
            idz = 0
            while z < self.scene_bounds.z_max:
                # Create an overlap sphere to determine if the cell is occupied.
                # Cast a ray to determine if the cell has a floor.
                cast_id = idx + (idz * 10000)
                self.commands.extend([{"$type": "send_overlap_capsule",
                                       "end": {"x": x, "y": capsule_half_height, "z": z},
                                       "radius": self._cell_size / 2,
                                       "position": {"x": x, "y": -capsule_half_height, "z": z},
                                       "id": cast_id},
                                      {"$type": "send_raycast",
                                       "origin": {"x": x, "y": OccupancyMap._RAYCAST_Y, "z": z},
                                       "destination": {"x": x, "y": -1, "z": z},
                                       "id": cast_id}])
                z += self._cell_size
                idz += 1
            x += self._cell_size
            idx += 1
        self._occupancy_map_size = (idx, idz)

    def get_occupancy_position(self, i: int, j: int) -> Tuple[float, float]:
        """
        Convert occupancy map indices to worldspace coordinates.
        This function can only be sent after first calling `self.generate()` and waiting at least one `controller.communicate()` call.:

        ```python
        from tdw.controller import Controller
        from tdw.tdw_utils import TDWUtils
        from tdw.add_ons.occupancy_map import OccupancyMap

        c = Controller(launch_build=False)
        o = OccupancyMap(cell_size=0.5)
        c.add_ons.append(o)
        c.communicate(TDWUtils.create_empty_room(12, 12))
        o.generate()
        c.communicate([])
        print(o.get_occupancy_position(4, 5))  # (-3.5, -3.0)
        c.communicate({"$type": "terminate"})
        ```

        :param i: The column index of self.occupancy_map
        :param j: The row index of self.occupancy_map.

        :return: A tuple: `self.occupancy_map[i][j]` converted into `(x, z)` worldspace coordinates.
        """

        if self.scene_bounds is None:
            raise Exception("The scene bounds haven't been generated and initialized (see documentation).")

        return self.scene_bounds.x_min + (i * self._cell_size), self.scene_bounds.z_min + (j * self._cell_size)

    def show(self) -> None:
        """
        Visualize the occupancy map by adding blue squares into the scene to mark free spaces.
        These blue squares don't interact with the physics engine.
        """

        if self.occupancy_map is None:
            raise Exception("The occupancy map hasn't been generated and initialized (see documentation).")
        for idx, idy in np.ndindex(self.occupancy_map.shape):
            if self.occupancy_map[idx][idy] != 0:
                continue
            x, z = self.get_occupancy_position(idx, idy)
            self.commands.append({"$type": "add_position_marker",
                                  "position": {"x": x, "y": 0.05, "z": z},
                                  "scale": self._cell_size * 0.9,
                                  "color": {"r": 0, "g": 0, "b": 1, "a": 1},
                                  "shape": "square"})

    def hide(self) -> None:
        """
        Remove all positions markers (the blue squares created by `self.show()`).
        """

        self.commands.append({"$type": "remove_position_markers"})

    def reset(self) -> None:
        """
        Reset the occupancy map. Call this when resetting a scene.
        """

        self.initialized = False
        self.occupancy_map = None
        self.scene_bounds = None
        self._occupancy_map_size = (0, 0)
        self._ignore_objects.clear()
