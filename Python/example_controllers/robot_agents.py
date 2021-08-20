from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.agent_manager import AgentManager
from tdw.add_ons.agents.robot import Robot


class RobotAgents(Controller):
    def run(self) -> None:
        ur5 = Robot(name="ur5",
                    position={"x": -1, "y": 0, "z": 0.5},
                    robot_id=0)
        ur10 = Robot(name="ur10",
                     position={"x": -3, "y": 0, "z": 0.5},
                     robot_id=1)
        am = AgentManager()
        am.agents.append(ur5)
        am.agents.append(ur10)
        self.add_ons.append(am)
        camera = ThirdPersonCamera(position={"x": -2.59, "y": 2, "z": -3.44},
                                   look_at={"x": -2, "y": 0.5, "z": 0})
        self.add_ons.append(camera)
        self.communicate([{"$type": "load_scene",
                           "scene_name": "ProcGenScene"},
                          TDWUtils.create_empty_room(12, 12)])
        ur5.set_joint_targets({ur5.static.joint_names["shoulder_link"]: 15,
                               ur5.static.joint_names["upper_arm_link"]: -45,
                               ur5.static.joint_names["forearm_link"]: 60})
        ur10.set_joint_targets({ur10.static.joint_names["shoulder_link"]: 80,
                                ur10.static.joint_names["upper_arm_link"]: -15,
                                ur10.static.joint_names["forearm_link"]: -20})
        while ur5.joints_are_moving() and ur10.joints_are_moving():
            self.communicate([])
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = RobotAgents()
    c.run()
