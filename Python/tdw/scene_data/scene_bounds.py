from typing import List, Optional
from tdw.output_data import OutputData, SceneRegions
from tdw.scene_data.region_bounds import RegionBounds, get_from_scene_regions


class SceneBounds:
    """
    Data for the scene bounds and its regions. In an interior scene, regions are equivalent to rooms.

    In order to initialize this object, the controller must have sent `send_scene_regions` to the build on the previous frame:

    ```python
    from tdw.controller import Controller
    from tdw.tdw_utils import TDWUtils
    from tdw.scene_data.scene_bounds import SceneBounds

    c = Controller()
    resp = c.communicate([TDWUtils.create_empty_room(12, 12),
                          {"$type": "send_scene_regions"}])
    scene_bounds = SceneBounds(resp=resp)
    ```
    """

    def __init__(self, resp: List[bytes]):
        """
        :param resp: The response from the build.
        """

        scene: Optional[SceneRegions] = None
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "sreg":
                scene = SceneRegions(resp[i])
                break
        assert scene is not None, "No scene regions data in response from build!"

        # Get the overall size of the scene.
        """:field
        Minimum x positional coordinate of the scene.
        """
        self.x_min: float = 1000
        """:field
        Maximum x positional coordinate of the scene.
        """
        self.x_max: float = 0
        """:field
        Minimum y positional coordinate of the scene.
        """
        self.y_min: float = 1000
        """:field
        Maximum y positional coordinate of the scene.
        """
        self.y_max: float = 0
        """:field
        Minimum z positional coordinate of the scene.
        """
        self.z_min: float = 1000
        """:field
        Maximum z positional coordinate of the scene.
        """
        self.z_max: float = 0
        """:field
        All of the regions in the scene.
        """
        self.regions: List[RegionBounds] = list()
        for i in range(scene.get_num()):
            e = get_from_scene_regions(scene_regions=scene, i=i)
            if e.x_min < self.x_min:
                self.x_min = e.x_min
            if e.y_min < self.y_min:
                self.y_min = e.y_min
            if e.z_min < self.z_min:
                self.z_min = e.z_min
            if e.x_max > self.x_max:
                self.x_max = e.x_max
            if e.y_max > self.y_max:
                self.y_max = e.y_max
            if e.z_max > self.z_max:
                self.z_max = e.z_max
            self.regions.append(e)
