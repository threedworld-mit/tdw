import numpy as np
from typing import Optional
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, StaticRobot, Robot


class RobotArm(Controller):
    """
    Add a robot to TDW and bend its arm.
    """

    def __init__(self, port: int = 1071, launch_build: bool = True):
        self.robot_id = 0
        super().__init__(port=port, launch_build=launch_build)

    def do_arm_motion(self) -> None:
        """
        Wait for the joints to stop moving.
        """

        done = False
        while not done:
            resp = self.communicate([])

            # Parse the output data for dynamic robot data.
            robot: Optional[Robot] = None
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                if r_id == "robo":
                    r = Robot(resp[i])
                    if r.get_id() == self.robot_id:
                        robot = r
                        break
            assert robot is not None, f"No robot data: {resp}"

            # Check if the joints are done moving.
            done = True
            for i in range(robot.get_num_body_parts()):
                if robot.get_body_part_sleeping(i):
                    continue
                if np.linalg.norm(robot.get_body_part_angular_velocity(i)) > 0.05:
                    done = False

    def run(self) -> None:
        self.start()

        # Create the scene. Add a robot.
        # Request static robot data for this frame only.
        # Request dynamic robot data per frame.
        commands = [TDWUtils.create_empty_room(12, 12),
                    {"$type": "add_robot",
                     "id": self.robot_id},
                    {"$type": "send_static_robots",
                     "frequency": "once"},
                    {"$type": "send_robots",
                     "frequency": "always"}]
        # Add an avatar to render the scene.
        commands.extend(TDWUtils.create_avatar(look_at=TDWUtils.VECTOR3_ZERO,
                                               position={"x": -0.881, "y": 0.836, "z": -1.396}))
        # This command is here just for demo purposes (so that the arm moves at a realistic speed).
        commands.append({"$type": "set_target_framerate",
                         "framerate": 30})

        resp = self.communicate(commands)

        # Parse the output data for static robot data.
        static_robot: Optional[StaticRobot] = None
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "srob":
                r = StaticRobot(resp[i])
                if r.get_id() == self.robot_id:
                    static_robot = r
                    break
        assert static_robot is not None, f"No static robot data: {resp}"

        # Get the IDs of the shoulder and the elbow.
        shoulder_id: Optional[int] = None
        elbow_id: Optional[int] = None
        for i in range(static_robot.get_num_body_parts()):
            b_id = static_robot.get_body_part_id(i)
            b_name = static_robot.get_body_part_name(i)
            if b_name == "Shoulder":
                shoulder_id = b_id
            elif b_name == "Elbow":
                elbow_id = b_id
        assert shoulder_id is not None, "Shoulder not found."
        assert elbow_id is not None, "Elbow not found"

        # Rotate the shoulder and the elbow for two motions.
        for angles in [[70, 90], [-30, -25]]:
            self.communicate([{"$type": "rotate_robot_joint_to",
                               "id": self.robot_id,
                               "joint_id": shoulder_id,
                               "force_limit": 5,
                               "angle": angles[0]},
                              {"$type": "rotate_robot_joint_to",
                               "id": self.robot_id,
                               "joint_id": elbow_id,
                               "force_limit": 5,
                               "angle": angles[1]}])
            # Wait for the joints to stop moving.
            self.do_arm_motion()


if __name__ == "__main__":
    RobotArm(launch_build=False).run()
