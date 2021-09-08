import numpy as np
from tdw.output_data import StaticRobot


class NonMoving:
    """
    Static data for a non-moving object attached to a robot (i.e. a sub-object mesh of a limb).

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
    # Print the ID and segmentation color of each non-moving body part.
    for body_part_id in robot.static.non_moving:
        print(body_part_id, robot.static.non_moving[body_part_id].segmentation_color)
    c.communicate({"$type": "terminate"})
    ```
    """

    def __init__(self, static_robot: StaticRobot, index: int):
        """
        :param static_robot: Static robot output data from the build.
        :param index: The index of this object in the list of non-moving objects.
        """

        """:field
        The ID of this object.
        """
        self.object_id: int = static_robot.get_non_moving_id(index)
        """:field
        The name of this object.
        """
        self.name: str = static_robot.get_non_moving_name(index)
        """:field
        The segmentation color of this joint as an `[r, g, b]` numpy array.
        """
        self.segmentation_color: np.array = np.array(static_robot.get_non_moving_segmentation_color(index))
