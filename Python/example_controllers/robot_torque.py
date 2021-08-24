from typing import Optional, Dict, List
import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, StaticRobot, Robot


class RobotTorque(Controller):
    """
    Add a robot to TDW and bend its arm.
    """

    def run(self) -> None:
        """
        Apply torques to the robot's shoulder and elbow.
        """

        robot_id = 0
        self.start()
        commands = [TDWUtils.create_empty_room(12, 12),
                    self.get_add_robot(name="ur5", robot_id=robot_id),
                    {"$type": "send_static_robots",
                     "frequency": "once"},
                    {"$type": "send_robots",
                     "frequency": "always"}]
        commands.extend(TDWUtils.create_avatar(look_at=TDWUtils.VECTOR3_ZERO,
                                               position={"x": -0.881, "y": 0.836, "z": -1.396}))
        resp = self.communicate(commands)
        # Parse the output data for static robot data.
        static_robot: Optional[StaticRobot] = None
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "srob":
                r = StaticRobot(resp[i])
                if r.get_id() == robot_id:
                    static_robot = r
                    break
        assert static_robot is not None, f"No static robot data: {resp}"
        shoulder_name = "shoulder_link"
        elbow_name = "forearm_link"
        # Get the IDs of the shoulder and the elbow.
        body_part_ids: Dict[str, int] = dict()
        for i in range(static_robot.get_num_joints()):
            b_id = static_robot.get_joint_id(i)
            b_name = static_robot.get_joint_name(i)
            body_part_ids[b_name] = b_id
        assert shoulder_name in body_part_ids
        assert elbow_name in body_part_ids
        # Apply torques.
        joint_ids: List[int] = [body_part_ids[shoulder_name], body_part_ids[elbow_name]]
        resp = self.communicate([{"$type": "add_torque_to_revolute",
                                  "id": robot_id,
                                  "joint_id": body_part_ids[shoulder_name],
                                  "torque": 500},
                                 {"$type": "add_torque_to_revolute",
                                  "id": robot_id,
                                  "joint_id": body_part_ids[elbow_name],
                                  "torque": -1000}])
        angles_0 = RobotTorque.get_angles(resp=resp, joint_ids=joint_ids)
        # Wait until the joints stop moving.
        moving = True
        while moving:
            moving = False
            resp = self.communicate([])
            angles_1 = RobotTorque.get_angles(resp=resp, joint_ids=joint_ids)
            for angle_0, angle_1 in zip(angles_0, angles_1):
                if np.abs(angle_0 - angle_1) > 0.001:
                    moving = True
                    break
            angles_0 = angles_1
        self.communicate({"$type": "terminate"})

    @staticmethod
    def get_angles(resp: List[bytes], joint_ids: List[int]) -> List[float]:
        """
        Get the current angles of the specified joints.

        :param resp: The response from the build.
        :param joint_ids: The IDs of the joints.

        :return: The angles of the joints.
        """

        angles: List[float] = list()
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "robo":
                robot = Robot(resp[i])
                for j in range(robot.get_num_joints()):
                    joint_id = robot.get_joint_id(j)
                    if joint_id in joint_ids:
                        angles.append(robot.get_joint_positions(j)[0])
        return angles


if __name__ == "__main__":
    RobotTorque(launch_build=False).run()
