from typing import List, Dict, Optional, Tuple
import numpy as np
from tdw.output_data import OutputData, Raycast
from tdw.add_ons.add_on import AddOn
from tdw.scene.scene_bounds import SceneBounds


class OccupancyMap(AddOn):
    def __init__(self):
        super().__init__()
        self.occupancy_map: Optional[np.array] = None
        self.scene_bounds: Optional[SceneBounds] = None
        self._cell_size: float = 0.49
        self._occupancy_map_size: Tuple[int, int] = (0, 0)
        self._y: float = 10

    def get_initialization_commands(self) -> List[dict]:
        return [{"$type": "send_environments"}]

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
        elif self.occupancy_map is None:
            # Re-show the roof.
            self.commands.append({"$type": "set_floorplan_roof",
                                  "show": True})
            # Generate the occupancy map.
            self.occupancy_map = np.zeros(shape=(self._occupancy_map_size[0] + 1, self._occupancy_map_size[1] + 1),
                                          dtype=int)
            # Group all of the raycasts by ID. Get data on whether they hit an object and if so at what height.
            hit_ids: List[int] = list()
            ys: Dict[int, List[float]] = dict()
            hits: Dict[int, List[float]] = dict()
            hit_objs: Dict[int, List[float]] = dict()
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                if r_id != "rayc":
                    continue
                raycast = Raycast(resp[i])
                raycast_y = raycast.get_point()[1]
                raycast_id = raycast.get_raycast_id()
                if raycast_id not in hit_ids:
                    hit_ids.append(raycast_id)
                    ys[raycast_id] = list()
                    hits[raycast_id] = list()
                    hit_objs[raycast_id] = list()
                is_hit = raycast.get_hit() and (not raycast.get_hit_object() or raycast_y > 0.01)
                hits[raycast_id].append(is_hit)
                if is_hit:
                    hit_object = raycast.get_hit_object()
                    ys[raycast_id].append(raycast_y)
                    if hit_object:
                        hit_objs[raycast_id].append(True)
            for hit_id in hit_ids:
                # This position is outside the environment.
                if len(ys[hit_id]) == 0 or len(hits[hit_id]) == 0 or \
                        len([h for h in hits[hit_id] if not h]) > 0 or max(ys[hit_id]) > self._y:
                    occupied = -1
                # This position is occupied. The max(ys) calculation will filter out very small objects.
                elif any(hit_objs[hit_id]) or max(ys[hit_id]) > 0.03:
                    occupied = 1
                # This position is free.
                else:
                    occupied = 0
                idx = hit_id % 10000
                idz = int((hit_id - (hit_id % 10000)) / 10000)
                self.occupancy_map[idx][idz] = occupied
                # Assume that the edges of the occupancy map are non-free.
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

    def generate(self, cell_size: float = 0.49, y: float = 10) -> None:
        """
        Generate an occupancy map.
        This function should only be called at least one controller.communicate() call after adding this add-on.
        The OccupancyMap then requires one more controller.communicate() call to create the occupancy map:

        ```python
        from tdw.controller import Controller
        from tdw.add_ons.occupancy_map import OccupancyMap

        c = Controller(launch_build=False)
        o = OccupancyMap()
        c.add_ons.append(o)
        c.communicate([])

        o.generate(cell_size=0.49, y=10)
        c.communicate([])
        print(o.occupancy_map)
        ```
        :param cell_size: The diameter of each cell of the occupancy map in meters.
        :param y: The height in meters from which the raycast will start.
        """

        if not self.initialized:
            print("Can't generate an occupancy map because this add-on hasn't initialized.\n"
                  "Wait at least one controller.communicate() call before calling occupancy_map.generate()")
            return
        self.occupancy_map = None
        self._cell_size = cell_size
        self._y = y
        self.commands.append({"$type": "set_floorplan_roof",
                              "show": False})
        # Spherecast to each point.
        x = self.scene_bounds.x_min
        idx = 0
        idz = 0
        while x < self.scene_bounds.x_max:
            z = self.scene_bounds.z_min
            idz = 0
            while z < self.scene_bounds.z_max:
                origin = {"x": x, "y": self._y, "z": z}
                destination = {"x": x, "y": -1, "z": z}
                # Spherecast the cell and raycast the center of the cell.
                # The center-raycast will let us know if this cell is partly out of bounds.
                raycast_id = idx + (idz * 10000)
                self.commands.extend([{"$type": "send_spherecast",
                                       "origin": origin,
                                       "destination": destination,
                                       "radius": self._cell_size / 2,
                                       "id": raycast_id},
                                      {"$type": "send_raycast",
                                       "origin": origin,
                                       "destination": destination,
                                       "id": raycast_id}])
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
        from tdw.add_ons.occupancy_map import OccupancyMap

        c = Controller(launch_build=False)
        o = OccupancyMap()
        c.add_ons.append(o)
        c.communicate([])

        o.generate(cell_size=0.49, y=10)
        c.communicate([])
        print(o.occupancy_map)
        ```

        :param i: The column index of self.occupancy_map
        :param j: The row index of self.occupancy_map.

        :return: `self.occupancy_map[i][j]` converted into x, z worldspace coordinates.
        """

        return self.scene_bounds.x_min + (i * self._cell_size), self.scene_bounds.z_min + (j * self._cell_size)
