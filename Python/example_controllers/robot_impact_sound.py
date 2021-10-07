from typing import List
import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.py_impact import PyImpact, ObjectInfo, AudioMaterial
from tdw.librarian import RobotLibrarian
from tdw.output_data import OutputData, StaticRobot, Robot


class RobotImpactSound(Controller):
    """
    Create impact sounds using PyImpact between a robot and an object.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.robot_id = self.get_unique_id()

    def run(self) -> None:
        robot_name = "ur5"
        self.start()
        resp = self.communicate([TDWUtils.create_empty_room(12, 12),
                                 self.get_add_robot(name=robot_name,
                                                    robot_id=self.robot_id),
                                 {"$type": "send_static_robots"}])
        # Get the joint names and IDs.
        joint_names_and_ids = dict()
        joint_masses = dict()
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "srob":
                srob = StaticRobot(resp[i])
                if srob.get_id() == self.robot_id:
                    for j in range(srob.get_num_joints()):
                        joint_name = srob.get_joint_name(j)
                        joint_names_and_ids[joint_name] = srob.get_joint_id(j)
                        joint_masses[joint_name] = srob.get_joint_mass(j)

        # Set the initial pose.
        commands = []
        robot_record = RobotLibrarian().get_record(robot_name)
        for joint_name in robot_record.targets:
            commands.append({"$type": "set_revolute_target",
                             "target": robot_record.targets[joint_name]["target"],
                             "joint_id": joint_names_and_ids[joint_name],
                             "id": self.robot_id})

        # Request dynamic robot data.
        commands.append({"$type": "send_robots",
                         "frequency": "always"})

        # Wait for the robot to arrive at the initial pose.
        resp = self.communicate(commands)
        self.wait_for_joints_to_stop_moving(resp=resp)

        # Initialize PyImpact.
        object_id = self.get_unique_id()
        object_names = {object_id: "rh10"}
        # Add the robot joints.
        for joint_name in joint_names_and_ids:
            object_names[joint_names_and_ids[joint_name]] = joint_name
        p = PyImpact()
        p.set_default_audio_info(object_names=object_names)

        # Add audio info for each joint.
        for joint_name in joint_names_and_ids:
            joint_audio = ObjectInfo(name=joint_name,
                                     amp=0.2,
                                     resonance=0.45,
                                     bounciness=0.6,
                                     mass=joint_masses[joint_name],
                                     library="",
                                     material=AudioMaterial.metal,
                                     size=2)
            p.object_info[joint_name] = joint_audio

        # Add the object. Enable collisions.
        commands = [self.get_add_object(model_name="rh10",
                                        object_id=object_id,
                                        position={"x": 0, "y": 6, "z": 0}),
                    {"$type": "send_collisions",
                     "enter": True,
                     "exit": True,
                     "stay": False,
                     "collision_types": ["obj"]},
                    {"$type": "send_rigidbodies",
                     "frequency": "always"}]
        # Create the avatar.
        avatar_id = "a"
        commands.extend(TDWUtils.create_avatar(position={"x": 0, "y": 2, "z": 2},
                                               look_at={"x": 0, "y": 0, "z": 0},
                                               avatar_id=avatar_id))
        commands.append({"$type": "add_audio_sensor",
                         "avatar_id": avatar_id})
        resp = self.communicate(commands)

        # Let the object fall.
        for i in range(200):
            commands = p.get_audio_commands(resp=resp, floor=AudioMaterial.wood_medium, wall=AudioMaterial.wood_medium)
            resp = self.communicate(commands)
        self.communicate({"$type": "terminate"})

    def get_joint_angles(self, resp: List[bytes]) -> List[float]:
        angles = []
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "robo":
                robo = Robot(resp[i])
                if robo.get_id() == self.robot_id:
                    for j in range(robo.get_num_joints()):
                        angles.extend(robo.get_joint_positions(j))
        return angles

    def wait_for_joints_to_stop_moving(self, resp: List[bytes]) -> None:
        angles_0 = self.get_joint_angles(resp=resp)
        done = False
        while not done:
            resp = self.communicate([])
            angles_1 = self.get_joint_angles(resp=resp)
            moving = False
            for a0, a1 in zip(angles_0, angles_1):
                if np.linalg.norm(a0 - a1) > 0.001:
                    moving = True
                    break
            if not moving:
                done = True
            angles_0 = angles_1[:]


if __name__ == "__main__":
    c = RobotImpactSound(launch_build=False)
    c.run()
