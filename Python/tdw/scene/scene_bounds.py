from typing import List, Optional
from tdw.output_data import OutputData, Environments
from tdw.scene.room_bounds import RoomBounds


class SceneBounds:
    """
    Data for the scene bounds and its rooms.

    In order to initialize this object, the controller must have sent `send_environments` to the build on the previous frame:

    ```python
    from tdw.controller import Controller
    from tdw.tdw_utils import TDWUtils
    from tdw.scene.scene_bounds import SceneBounds

    c = Controller()
    c.start()
    resp = c.communicate([TDWUtils.create_empty_room(12, 12),
                          {"$type": "send_environments"}])
    scene_bounds = SceneBounds(resp=resp)
    ```
    """

    def __init__(self, resp: List[bytes]):
        """
        :param resp: The response from the build.
        """

        env: Optional[Environments] = None
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "envi":
                env = Environments(resp[i])
                break
        assert env is not None, "No scene data in response from build!"

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
        All of the rooms in the scene.
        """
        self.rooms: List[RoomBounds] = list()
        for i in range(env.get_num()):
            e = RoomBounds(env=env, i=i)
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
            self.rooms.append(e)
