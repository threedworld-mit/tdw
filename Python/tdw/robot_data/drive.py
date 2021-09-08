from typing import Tuple
from tdw.output_data import StaticRobot


class Drive:
    """
    Static data for a joint drive.


    ```python
    from tdw.controller import Controller
    from tdw.tdw_utils import TDWUtils
    from tdw.add_ons.robot import Robot

    c = Controller()
    # Add a robot.
    robot = Robot(name="ur5",
                  position={"x": -1, "y": 0, "z": 0.5},
                  robot_id=0)
    c.add_ons.append(robot)
    # Initialize the scene_data.
    c.communicate([{"$type": "load_scene",
                    "scene_name": "ProcGenScene"},
                   TDWUtils.create_empty_room(12, 12)])

    # Get each joint.
    for joint_id in robot.static.joints:
        # Get each drive.
        for drive_axis in robot.static.joints[joint_id].drives:
            drive = robot.static.joints[joint_id].drives[drive_axis]
            print(drive_axis, drive.force_limit, drive.damping, drive.stiffness)
    c.communicate({"$type": "terminate"})
    ```
    """

    def __init__(self, sr: StaticRobot, joint_index: int, drive_index: int):
        """
        :param sr: The StaticRobot output data.

        :param joint_index: The index of the joint in the output data that this drive belongs to.
        :param drive_index: The index of this drive in the joint data.
        """

        """:field
        The axis of rotation. Can be `"x"`, `"y"`, or `"z"`.
        """
        self.axis: str = sr.get_joint_drive_axis(joint_index, drive_index)
        """:field
        Tuple: The lower and upper limits of the drive rotation in degrees.
        """
        self.limits: Tuple[float, float] = (sr.get_joint_drive_lower_limit(joint_index, drive_index),
                                            sr.get_joint_drive_upper_limit(joint_index, drive_index))
        """:field
        The limit of how much force can be applied to the drive.
        """
        self.force_limit = sr.get_joint_drive_force_limit(joint_index, drive_index)
        """:field
        The damping value.
        """
        self.damping = sr.get_joint_drive_damping(joint_index, drive_index)
        """:field
        The stiffness value.
        """
        self.stiffness = sr.get_joint_drive_stiffness(joint_index, drive_index)
