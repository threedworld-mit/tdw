from typing import List, Dict
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.add_on import AddOn
from tdw.output_data import OutputData, StaticRigidbodies, Bounds, StaticRobot


class NavMesh(AddOn):
    """
    Create a NavMesh and make objects NavMeshObstacles.

    Each NavMeshObstacle will be set according to the position, size, and kinematic state of the object.

    This add-on requires 2 `communicate(commands)` calls to initialize.
    """

    def __init__(self, exclude_objects: List[int] = None, max_y: float = 0.1, exclude_area: float = 0.05,
                 small_area: float = 1, small_area_scale: float = 1, large_area_scale: float = 1.25,
                 roundness_threshold: float = 0.95):
        """
        :param exclude_objects: A list of object IDs to exclude. These won't be made into NavMeshObstacles.
        :param max_y: If an object's y positional value is greater than this, the object won't be made into a NavMeshObstacle.
        :param exclude_area: If an object's (x, z) area is less than this, the object won't be made into a NavMeshObstacle.
        :param small_area: If an object's (x, z) area is smaller than this, its NavMeshObstacle will be scaled.
        :param small_area_scale: If the object has a small area (see above), its NavMeshObstacle will be scaled by this factor.
        :param large_area_scale: If the object has a large area (see above), its NavMeshObstacle will be scaled by this factor.
        :param roundness_threshold: If the ration of the x and z extents of the object is less than this, the NavMeshObstacle will carve a box shape. Otherwise, it will carve a capsule shape.
        """

        super().__init__()
        if exclude_objects is None:
            self._exclude_objects: List[int] = list()
        else:
            self._exclude_objects = exclude_objects
        self._made_nav_mesh_obstacles: bool = False
        self._max_y: float = max_y
        self._small_area: float = small_area
        self._small_area_scale: float = small_area_scale
        self._large_area_scale: float = large_area_scale
        self._exclude_area: float = exclude_area
        self._roundness_threshold: float = roundness_threshold

    def get_initialization_commands(self) -> List[dict]:
        return [{"$type": "send_bounds",
                 "frequency": "always"},
                {"$type": "send_static_rigidbodies",
                 "frequency": "once"},
                {"$type": "send_static_robots",
                 "frequency": "once"}]

    def on_send(self, resp: List[bytes]) -> None:
        if self._made_nav_mesh_obstacles:
            return
        self._made_nav_mesh_obstacles = True
        areas: Dict[int, float] = dict()
        kinematics: Dict[int, bool] = dict()
        boxes: Dict[int, bool] = dict()
        robots: List[int] = list()
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            # Use bounds data to sort objects by position and area.
            if r_id == "boun":
                bounds = Bounds(resp[i])
                for j in range(bounds.get_num()):
                    bottom = bounds.get_bottom(j)[1]
                    object_id = bounds.get_id(j)
                    # Objects below the floor, objects that are too high up, or excluded objects.
                    if bottom <= -0.1 or bottom > self._max_y or object_id in self._exclude_objects:
                        continue
                    # Get the area.
                    extents = TDWUtils.get_bounds_extents(bounds, j)
                    area = extents[0] * extents[2]
                    # Ignore small objects.
                    if area < self._exclude_area:
                        continue
                    # Remember the area.
                    areas[object_id] = area
                    # Get the roundness
                    if extents[0] < extents[2]:
                        roundness = extents[0] / extents[2]
                    else:
                        roundness = extents[2] / extents[0]
                    boxes[object_id] = roundness < self._roundness_threshold
            # Use static rigidbodies data to sort objects by kinematic state.
            elif r_id == "srig":
                static_rigidbodies = StaticRigidbodies(resp[i])
                for j in range(static_rigidbodies.get_num()):
                    kinematics[static_rigidbodies.get_id(j)] = static_rigidbodies.get_kinematic(j)
            # Ignore all robots.
            elif r_id == "srob":
                robots.append(StaticRobot(resp[i]).get_id())
        for object_id in areas:
            if object_id not in kinematics:
                continue
            # Make the obstacle. For smaller objects, make the obstacle half-scale.
            self.commands.append({"$type": "make_nav_mesh_obstacle",
                                  "id": object_id,
                                  "carve_type": "all",
                                  "scale": self._small_area_scale if areas[object_id] < self._small_area and not kinematics[object_id] else self._large_area_scale,
                                  "shape": "box" if boxes[object_id] else "capsule"})
        # Bake the NavMesh.
        self.commands.append({"$type": "bake_nav_mesh",
                              "ignore": robots})

    def reset(self, exclude_objects: List[int] = None) -> None:
        """
        Call this to reset the add-on.

        :param exclude_objects: A list of object IDs to exclude. These won't be made into NavMeshObstacles.
        """

        self.initialized = False
        self._made_nav_mesh_obstacles = False
        self._exclude_objects.clear()
        if exclude_objects is not None:
            self._exclude_objects.extend(exclude_objects)
