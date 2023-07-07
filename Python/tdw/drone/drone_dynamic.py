from typing import List
import numpy as np
from tdw.output_data import OutputData, Drones
from tdw.agent_data.agent_dynamic import AgentDynamic


class DroneDynamic(AgentDynamic):
    """
    Dynamic data for a drone that can change per `communicate()` call (such as the position of the drone).
    """

    def __init__(self, resp: List[bytes], drone_id: int, frame_count: int):
        """
        :param resp: The response from the build, which we assume contains `drone` output data.
        :param drone_id: The ID of this drone.
        :param frame_count: The current frame count.
        """

        super().__init__(resp=resp, agent_id=drone_id, frame_count=frame_count)
        """:field
        If True, the ray that was cast down from the drone hit something.
        """
        self.raycast_hit: bool = False
        """:field
        The point that the ray that was cast down from the drone hit. Ignore this if `self.raycast_hit == False`.
        """
        self.raycast_point: np.ndarray = np.zeros(shape=3)
        """:field
        If True, the drone's motor is on.
        """
        self.motor_on: bool = False

        self.avatar_id = str(drone_id)
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            # Get the data for this drone.
            if r_id == "dron":
                drones = Drones(resp[i])
                for j in range(drones.get_num()):
                    if self._agent_id == drones.get_id(j):
                        self.raycast_hit = drones.get_raycast_hit(j)
                        if self.raycast_hit:
                            self.raycast_point = drones.get_raycast(j)
                        self.motor_on = drones.get_motor_on(j)
