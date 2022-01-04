from time import sleep
import numpy as np
from typing import Optional, Dict, List
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, StaticRobot, Robot


class RobotArm(Controller):
    """
    Control a UR5 robot with low-level commands.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.robot_id = 0

    def get_robot(self, resp: List[bytes]) -> Robot:
        """
        :param resp: The response from the build.

        :return: `Robot` output data.
        """

        robot: Optional[Robot] = None
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "robo":
                r = Robot(resp[i])
                if r.get_id() == self.robot_id:
                    robot = r
                    break
        return robot

    @staticmethod
    def get_joint_angles(robot: Robot) -> List[float]:
        """
        :param robot: The `Robot` output data.

        :return: The angles of each joint.
        """

        angles: List[float] = list()
        for i in range(robot.get_num_joints()):
            # Prismatic and revolute joints have 1 angle. Spherical joints have 3 angles. Fixed joints have 0 angles.
            angles.extend(robot.get_joint_positions(i))
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
                    {"$type": "send_robots",
                     "frequency": "always"}]
        # Add an avatar to render the scene (just for demo purposes).
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
            robot = self.get_robot(resp=resp)
            angles_0 = self.get_joint_angles(robot=robot)
            # Wait for the joints to stop moving.
            moving = True
            while moving:
                robot = self.get_robot(resp=self.communicate([]))
                angles_1 = self.get_joint_angles(robot=robot)
                # Compare the current joint angles to the angles of the previous frame.
                moving = False
                for angle_0, angle_1 in zip(angles_0, angles_1):
                    if np.abs(angle_0 - angle_1) > 0.001:
                        moving = True
                        break
                angles_0 = angles_1
        sleep(3)
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    RobotArm(launch_build=False).run()
