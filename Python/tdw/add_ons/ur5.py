import numpy as np
from ikpy.link import OriginLink, URDFLink, Link
from typing import List
from tdw.add_ons.robot_arm import RobotArm


class UR5(RobotArm):
    """
    A UR5 robot arm with an inverse kinematics (IK) solver.
    """

    def _get_name(self) -> str:
        return "ur5"

    def _get_joint_order(self) -> List[str]:
        return ["shoulder_link", "upper_arm_link", "forearm_link", "wrist_1_link", "wrist_2_link",
                "wrist_3_link"]

    def _get_links(self) -> List[Link]:
        bounds = (np.deg2rad(-360), np.deg2rad(360))
        orientation = np.array([0, 0, 0])
        return [OriginLink(),
                URDFLink(name="shoulder_link",
                         translation_vector=np.array([0, 0.08915899, 0]),
                         orientation=orientation,
                         rotation=np.array([0, -1, 0]),
                         bounds=bounds),
                URDFLink(name="upper_arm_link",
                         translation_vector=np.array([-0.13585, 0, 0]),
                         orientation=orientation,
                         rotation=np.array([1, 0, 0]),
                         bounds=bounds),
                URDFLink(name="forearm_link",
                         translation_vector=np.array([0.1196999, 0, 0.425001]),
                         orientation=orientation,
                         rotation=np.array([1, 0, 0]),
                         bounds=bounds),
                URDFLink(name="wrist_1_link",
                         translation_vector=np.array([0, 0, 0.3922516]),
                         orientation=orientation,
                         rotation=np.array([1, 0, 0]),
                         bounds=bounds),
                URDFLink(name="wrist_2_link",
                         translation_vector=np.array([-0.093, 0, 0]),
                         orientation=orientation,
                         rotation=np.array([0, -1, 0]),
                         bounds=bounds),
                URDFLink(name="wrist_3_link",
                         translation_vector=np.array([0, -0.09465025, 0]),
                         orientation=orientation,
                         rotation=None)]
