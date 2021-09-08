from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.robot import Robot


class RobotAgents(Controller):
    """
    Add multiple robots to the scene_data.
    """

    def run(self) -> None:
        # Add two robots.
        ur5 = Robot(name="ur5",
                    position={"x": -1, "y": 0, "z": 0.5},
                    robot_id=0)
        ur10 = Robot(name="ur10",
                     position={"x": -3, "y": 0, "z": 0.5},
                     robot_id=1)
        # Add a third-person camera.
        camera = ThirdPersonCamera(position={"x": -2.59, "y": 2, "z": -3.44},
                                   look_at={"x": -2, "y": 0.5, "z": 0})
        self.add_ons.extend([ur5, ur10, camera])

        # Initialize the scene_data.
        self.communicate([{"$type": "load_scene",
                           "scene_name": "ProcGenScene"},
                          TDWUtils.create_empty_room(12, 12)])

        # Set joint targets for both robots.
        shoulder: str = "shoulder_link"
        upper_arm: str = "upper_arm_link"
        forearm: str = "forearm_link"
        ur5.set_joint_targets({ur5.static.joint_ids_by_name[shoulder]: 15,
                               ur5.static.joint_ids_by_name[upper_arm]: -45,
                               ur5.static.joint_ids_by_name[forearm]: 60})
        ur10.set_joint_targets({ur10.static.joint_ids_by_name[shoulder]: 80,
                                ur10.static.joint_ids_by_name[upper_arm]: -15,
                                ur10.static.joint_ids_by_name[forearm]: -20})
        # Wait for both robots to stop moving.
        while ur5.joints_are_moving() and ur10.joints_are_moving():
            self.communicate([])
        # Set new joint targets.
        ur5.set_joint_targets({ur5.static.joint_ids_by_name[forearm]: 0})
        ur10.set_joint_targets({ur10.static.joint_ids_by_name[forearm]: 60})
        # Wait for just the UR5 robot to stop moving.
        while ur5.joints_are_moving():
            self.communicate([])
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = RobotAgents()
    c.run()
