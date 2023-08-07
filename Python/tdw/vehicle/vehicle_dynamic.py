from typing import List
import numpy as np
from tdw.agent_data.agent_dynamic import AgentDynamic
from tdw.object_data.rigidbody import Rigidbody
from tdw.output_data import OutputData, Rigidbodies


class VehicleDynamic(AgentDynamic):
    """
    Dynamic data for a vehicle that can change per `communicate()` call (such as the position of the vehicle).
    """

    def __init__(self, resp: List[bytes], agent_id: int, frame_count: int):
        super().__init__(resp=resp, agent_id=agent_id, frame_count=frame_count)
        """:field
        The [`Rigidbody`](../object_data/rigidbody.md) (velocity and angular velocity) of the vehicle.
        """
        self.rigidbody: Rigidbody = Rigidbody(velocity=np.zeros(shape=3),
                                              angular_velocity=np.zeros(shape=3),
                                              sleeping=False)
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "rigi":
                rigidbodies = Rigidbodies(resp[i])
                for j in range(rigidbodies.get_num()):
                    if rigidbodies.get_id(j) == agent_id:
                        self.rigidbody.velocity = rigidbodies.get_velocity(j)
                        self.rigidbody.angular_velocity = rigidbodies.get_angular_velocity(j)
                        self.rigidbody.sleeping = rigidbodies.get_sleeping(j)
