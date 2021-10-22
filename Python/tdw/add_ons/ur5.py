import numpy as np
from ikpy.chain import Chain
from ikpy.link import OriginLink, URDFLink, Link
from tdw.add_ons.robot import Robot
from typing import List, Dict, Union
from tdw.tdw_utils import TDWUtils


class UR5(Robot):
    JOINT_ORDER: List[str] = ["shoulder_link", "upper_arm_link", "forearm_link", "wrist_1_link", "wrist_2_link",
                              "wrist_3_link"]

    def __init__(self, robot_id: int = 0, position: Dict[str, float] = None, rotation: Dict[str, float] = None):
        super().__init__(name="ur5", robot_id=robot_id, position=position, rotation=rotation)
        self.chain: Chain = Chain(name="ur5", links=self.get_links())

    def reach_for(self, target: Union[Dict[str, float], np.array]) -> None:
        # Get the current angles of the joints.
        initial_angles = [0]
        for joint_name in UR5.JOINT_ORDER:
            initial_angles.append(self.dynamic.joints[self.static.joint_ids_by_name[joint_name]].angles[0])
        initial_angles.append(0)
        initial_angles = np.radians(initial_angles)
        if isinstance(target, dict):
            target = TDWUtils.vector3_to_array(target)
        angles = self.chain.inverse_kinematics(target_position=target,
                                               initial_position=initial_angles)
        # Convert the IK solution to degrees. Remove the origin link.
        angles = [float(np.rad2deg(angle)) for angle in angles[1:-1]]
        # Convert the angles to a dictionary of joint targets.
        targets = dict()
        for joint_name, angle in zip(UR5.JOINT_ORDER, angles):
            targets[self.static.joint_ids_by_name[joint_name]] = angle
        self.set_joint_targets(targets=targets)

    def get_links(self) -> List[Link]:
        return [OriginLink(),
                URDFLink(name="shoulder_link",
                         translation_vector=np.array([0, 0.08915899, 0]),
                         orientation=np.array([0, 0, 0]),
                         rotation=np.array([0, -1, 0]),
                         bounds=(np.deg2rad(-360), np.deg2rad(360))),
                URDFLink(name="upper_arm_link",
                         translation_vector=np.array([-0.13585, 0, 0]),
                         orientation=np.array([0, 0, 0]),
                         rotation=np.array([-1, 0, 0]),
                         bounds=(np.deg2rad(-360), np.deg2rad(360))),
                URDFLink(name="forearm_link",
                         translation_vector=np.array([0.1196999, 0.425001, 0]),
                         orientation=np.array([0, 0, 0]),
                         rotation=np.array([-1, 0, 0]),
                         bounds=(np.deg2rad(-360), np.deg2rad(360))),
                URDFLink(name="wrist_1_link",
                         translation_vector=np.array([0, 0.3922516, 0]),
                         orientation=np.array([0, 0, 0]),
                         rotation=np.array([-1, 0, 0]),
                         bounds=(np.deg2rad(-360), np.deg2rad(360))),
                URDFLink(name="wrist_2_link",
                         translation_vector=np.array([-0.093, 0, 0]),
                         orientation=np.array([0, 0, 0]),
                         rotation=np.array([0, -1, 0]),
                         bounds=(np.deg2rad(-360), np.deg2rad(360))),
                URDFLink(name="wrist_3_link",
                         translation_vector=np.array([0, 0.09465025, 0]),
                         orientation=np.array([0, 0, 0]),
                         rotation=np.array([-1, 0, 0]),
                         bounds=(np.deg2rad(-360), np.deg2rad(360))),
                URDFLink(name="end_effector",
                         translation_vector=np.array([-0.0802, 0, 0]),
                         orientation=np.array([0, 0, 0]),
                         rotation=None)]
