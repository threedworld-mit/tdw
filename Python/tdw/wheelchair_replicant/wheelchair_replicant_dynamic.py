from typing import List, Dict
import numpy as np
from tdw.output_data import OutputData, Wheelchairs
from tdw.object_data.rigidbody import Rigidbody
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.wheelchair_replicant.wheel_position import WheelPosition
from tdw.wheelchair_replicant.wheel import Wheel


class WheelchairReplicantDynamic(ReplicantDynamic):
    """
    Dynamic data for a WheelchairReplicant that can change per `communicate()` call (such as the position of the WheelchairReplicant).
    """

    def __init__(self, resp: List[bytes], replicant_id: int, frame_count: int):
        super().__init__(resp=resp, replicant_id=replicant_id, frame_count=frame_count)
        """:field
        Data for each wheel: motor torque, brake torque, and steer angle. Key = A [`WheelPosition`](wheel_position.md). Value = A [`Wheel`](wheel.md).
        """
        self.wheels: Dict[WheelPosition, Wheel] = dict()
        """:field
        Physics [`Rigidbody`](../object_data/rigidbody.md) data for the wheelchair.
        """
        self.rigidbody: Rigidbody = Rigidbody(velocity=np.zeros(3), angular_velocity=np.zeros(3), sleeping=False)
        # Get the wheel data.
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "whch":
                wheelchairs = Wheelchairs(resp[i])
                for j in range(wheelchairs.get_num()):
                    if wheelchairs.get_id(j) == replicant_id:
                        # Set the Rigidbody.
                        self.rigidbody.velocity = wheelchairs.get_velocity(j)
                        self.rigidbody.angular_velocity = wheelchairs.get_angular_velocity(j)
                        self.rigidbody.sleeping = wheelchairs.get_sleeping(j)
                        # Set the wheels.
                        for k in range(4):
                            wheel_data: np.ndarray = wheelchairs.get_wheel(j, k)
                            self.wheels[WheelPosition(k)] = Wheel(motor_torque=float(wheel_data[0]),
                                                                  brake_torque=float(wheel_data[1]),
                                                                  steer_angle=float(wheel_data[2]))
                        break
                break
