from typing import Optional, Dict
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, StaticRobot


class RobotTorque(Controller):
    """
    Add a robot to TDW and bend its arm.
    """

    def run(self) -> None:
        robot_id = 0
        self.start()
        commands = [TDWUtils.create_empty_room(12, 12),
                    self.get_add_robot(name="ur5", robot_id=robot_id),
                    {"$type": "send_static_robots",
                     "frequency": "once"}]
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
        self.communicate([{"$type": "add_torque_to_revolute",
                           "id": robot_id,
                           "joint_id": body_part_ids[shoulder_name],
                           "torque": 500},
                          {"$type": "add_torque_to_revolute",
                           "id": robot_id,
                           "joint_id": body_part_ids[elbow_name],
                           "torque": -1000}])
        for i in range(500):
            self.communicate([])
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    RobotTorque(launch_build=False).run()
