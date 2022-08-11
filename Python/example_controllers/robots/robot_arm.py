from time import sleep
import numpy as np
from typing import Optional, Dict, List
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, StaticRobot, DynamicRobots


class RobotArm(Controller):
    """
    Control a UR5 robot with low-level commands.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.robot_id = 0
        # The index of this robot's joints in `DynamicRobots` output data.
        self.joint_indices: np.ndarray = np.array([0], dtype=int)

    @staticmethod
    def get_dynamic_robots(resp: List[bytes]) -> DynamicRobots:
        """
        :param resp: The response from the build.

        :return: `DynamicRobots` output data.
        """

        robots: Optional[DynamicRobots] = None
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "drob":
                robots = DynamicRobots(resp[i])
                break
        return robots

    def get_joint_angles(self, robots: DynamicRobots) -> List[float]:
        """
        :param robots: The `DynamicRobot` output data.

        :return: The angles of each joint.
        """

        angles = []
        for id_index in self.joint_indices:
            # id_index is a pair of integers. id_index[0] is the joint ID. id_index[1] is the index.
            index = id_index[1]
            angles.extend(robots.get_joint_angles(index))
        return angles

    def run(self) -> None:
        robot_id = 0
        # Create the scene. Add a robot.
        # Request static robot data for this frame only.
        # Request dynamic robot data per frame.
        commands = [TDWUtils.create_empty_room(12, 12),
                    self.get_add_robot(name="ur5", robot_id=robot_id),
                    {"$type": "send_static_robots",
                     "frequency": "once"},
                    {"$type": "send_dynamic_robots",
                     "frequency": "always"}]
        # Add an avatar to render the scene (just for demo purposes).
        commands.extend(TDWUtils.create_avatar(look_at=TDWUtils.VECTOR3_ZERO,
                                               position={"x": -0.881, "y": 0.836, "z": -1.396}))
        # Send the commands.
        resp = self.communicate(commands)
        # Parse the output data for static robot data.
        static_robot: Optional[StaticRobot] = None
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "srob":
                r = StaticRobot(resp[i])
                if r.get_id() == robot_id:
                    static_robot = r
                    self.joint_indices = static_robot.get_joint_indices()
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
        # Rotate the shoulder and the elbow for two motions.
        # The values in this array are for the angle that the [shoulder, elbow] should rotate to per action.
        # For more complex actions, you will probably want to organize your commands differently.
        for angles in [[70, -45], [-35, -90]]:
            resp = self.communicate([{"$type": "set_revolute_target",
                                      "id": robot_id,
                                      "joint_id": body_part_ids[shoulder_name],
                                      "target": angles[0]},
                                     {"$type": "set_revolute_target",
                                      "id": robot_id,
                                      "joint_id": body_part_ids[elbow_name],
                                      "target": angles[1]}])
            # Get the robot output data.
            robots = self.get_dynamic_robots(resp=resp)
            angles_0 = self.get_joint_angles(robots=robots)
            # Wait for the joints to stop moving.
            moving = True
            while moving:
                resp = self.communicate([])
                robots = self.get_dynamic_robots(resp=resp)
                angles_1 = self.get_joint_angles(robots=robots)
                # Compare the current joint angles to the angles of the previous frame.
                moving = False
                for angle_0, angle_1 in zip(angles_0, angles_1):
                    if np.linalg.norm(angle_0 - angle_1) > 0.001:
                        moving = True
                        break
                angles_0 = angles_1
        sleep(3)
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    RobotArm().run()
