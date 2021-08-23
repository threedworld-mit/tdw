from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from overrides import final
import numpy as np
from tdw.add_ons.agents.agent import Agent
from tdw.add_ons.agents.robot_data.robot_static import RobotStatic
from tdw.add_ons.agents.robot_data.robot_dynamic import RobotDynamic


class RobotBase(Agent, ABC):
    """
    Abstract base class for robot agents.
    """

    """:class_var
    If a joint has moved less than this many degrees (revolute or spherical) or meters (prismatic) since the previous frame, it is considered to be not moving for the purposes of determining which joints are moving.
    """
    NON_MOVING: float = 0.001

    def __init__(self, robot_id: int = 0, position: Dict[str, float] = None, rotation: Dict[str, float] = None):
        """
        :param robot_id: The ID of the robot.
        :param position: The position of the robot. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param rotation: The rotation of the robot in Euler angles (degrees). If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        """

        super().__init__()

        if position is None:
            """:field
            The initial position of the robot.
            """
            self.initial_position: Dict[str, float] = {"x": 0, "y": 0, "z": 0}
        else:
            self.initial_position: Dict[str, float] = position
        if rotation is None:
            """:field
            The initial rotation of the robot.
            """
            self.initial_rotation: Dict[str, float] = {"x": 0, "y": 0, "z": 0}
        else:
            self.initial_rotation: Dict[str, float] = rotation
        """:field
        The ID of this robot.
        """
        self.robot_id: int = robot_id
        """:field
        Static robot data.
        """
        self.static: Optional[RobotStatic] = None
        """:field
        Dynamic robot data.
        """
        self.dynamic: Optional[RobotDynamic] = None

    def get_initialization_commands(self) -> List[dict]:
        return [self._get_add_robot_command(),
                {"$type": "send_static_robots",
                 "frequency": "once"},
                {"$type": "send_robots",
                 "frequency": "always"}]

    def joints_are_moving(self, joint_ids: List[int] = None) -> bool:
        """
        :param joint_ids: A list of joint IDs to check for movement. If `None`, check all joints for movement.

        :return: True if the joints are moving.
        """

        if joint_ids is None:
            joint_ids = self.dynamic.joints.keys()
        for joint_id in joint_ids:
            if self.dynamic.joints[joint_id].moving:
                return True
        return False

    @abstractmethod
    def _get_add_robot_command(self) -> dict:
        """
        :return: A command to add the robot.
        """

        raise Exception()

    @final
    def _set_joints_moving(self, dynamic: RobotDynamic) -> RobotDynamic:
        """
        Set the state of the dynamic data regarding whether the joints are currently moving.

        :param dynamic: The dynamic data.

        :return: The updated dynamic data.
        """

        if self.dynamic is not None:
            # Check which joints are still moving.
            for joint_id in dynamic.joints:
                dynamic.joints[joint_id].moving = False
                for angle_0, angle_1 in zip(self.dynamic.joints[joint_id].angles, dynamic.joints[joint_id].angles):
                    if np.linalg.norm(angle_1 - angle_0) > RobotBase.NON_MOVING:
                        dynamic.joints[joint_id].moving = True
                        break
        else:
            for joint_id in dynamic.joints:
                dynamic.joints[joint_id].moving = True
        return dynamic
