from typing import Dict
import numpy as np
from tdw.output_data import StaticRobot
from tdw.robot_data.drive import Drive
from tdw.robot_data.joint_type import JointType


class JointStatic:
    """
    Static robot joint data.
    """

    def __init__(self, static_robot: StaticRobot, static_index: int, dynamic_index: int):
        """
        :param static_robot: Static robot output data from the build.
        :param static_index: The index of this joint in the list of joints.
        :param dynamic_index: The index in the overall list of joints in `DynamicRobots` output data.
        """

        """:field
        The ID of this joint.
        """
        self.joint_id: int = static_robot.get_joint_id(static_index)
        """:field
        The name of the joint.
        """
        self.name: str = static_robot.get_joint_name(static_index)
        """:field
        [The type of joint.](joint_type.md)
        """
        self.joint_type: JointType = JointType[static_robot.get_joint_type(static_index)]
        """:field
        The segmentation color of this joint as an `[r, g, b]` numpy array.
        """
        self.segmentation_color: np.ndarray = np.array(static_robot.get_joint_segmentation_color(static_index))
        """:field
        The mass of this joint.
        """
        self.mass: float = static_robot.get_joint_mass(static_index)
        """:field
        If True, this joint is immovable.
        """
        self.immovable: bool = static_robot.get_is_joint_immovable(static_index)
        """:field
        If True, this is the root joint.
        """
        self.root: bool = static_robot.get_is_joint_root(static_index)
        """:field
        The ID of this joint's parent joint. Ignore if `self.root == True`.
        """
        self.parent_id: int = static_robot.get_joint_parent_id(static_index)
        """:field
        A dictionary of [Drive data](drive.md) for each of the robot's joints. Key = The drive axis (`"x"`, `"y"`, or `"z"`).
        """
        self.drives: Dict[str, Drive] = dict()
        for i in range(static_robot.get_num_joint_drives(static_index)):
            drive = Drive(sr=static_robot, joint_index=static_index, drive_index=i)
            self.drives[drive.axis] = drive
        """:field
        The number of degrees of freedom. This is equivalent to len(self.drives).
        """
        self.num_dof: int = len(self.drives)
        """:field
        The index in the overall list of joints in `DynamicRobots` output data. This is used internally; you almost always want `self.joint_id`.
        """
        self.dynamic_index: int = dynamic_index
