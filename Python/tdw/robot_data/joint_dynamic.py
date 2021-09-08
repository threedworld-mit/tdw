import numpy as np
from tdw.output_data import Robot


class JointDynamic:
    """
    Dynamic info for a joint that can change per-frame, such as its current position.


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
    # Initialize the scene.
    c.communicate([{"$type": "load_scene",
                    "scene_name": "ProcGenScene"},
                   TDWUtils.create_empty_room(12, 12)])

    # Get the current position of each joint.
    for joint_id in robot.dynamic.joints:
        print(joint_id, robot.dynamic.joints[joint_id].position)
    c.communicate({"$type": "terminate"})
    ```
    """

    def __init__(self, robot: Robot, joint_index: int):
        """
        :param robot: The `Robot` output data from the build.
        :param joint_index: The index of the data for this joint.
        """

        """:field
        The ID of this joint.
        """
        self.joint_id: int = robot.get_joint_id(joint_index)
        """:field
        The worldspace position of this joint as an `[x, y, z]` numpy array.
        """
        self.position: np.array = np.array(robot.get_joint_position(joint_index))
        """:field
        The angles of each axis of the joint in degrees. For prismatic joints, you need to convert this from degrees to radians in order to get the correct distance in meters.
        """
        self.angles: np.array = robot.get_joint_positions(joint_index)
        """:field
        If True, this joint is currently moving.
        """
        self.moving: bool = False
