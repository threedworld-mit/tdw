from typing import Optional, List, Dict, Union
import numpy as np
from tdw.librarian import RobotLibrarian, RobotRecord
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.add_on import AddOn
from tdw.add_ons.robots.robot_static import RobotStatic
from tdw.add_ons.robots.robot_dynamic import RobotDynamic


class Robot(AddOn):
    ROBOT_LIBRARIAN: RobotLibrarian = RobotLibrarian()

    def __init__(self, robot: str, position: Dict[str, float] = None, rotation: Dict[str, float] = None,
                 robot_id: int = 0, source: Union[RobotLibrarian, RobotRecord, str] = None):
        """
        :param robot_id: The ID of the robot.
        """

        super().__init__()
        """:field
        The ID of the robot.
        """
        self.robot_id: int = robot_id
        """:field
        [Static data](robots/robot_static.md) for this robot.
        """
        self.static: Optional[RobotStatic] = None
        """:
        [Dynamic data](robots/robot_dynamic.md) for this robot.
        """
        self.dynamic: Optional[RobotDynamic] = None

        url: str
        if source is None:
            url = Robot.ROBOT_LIBRARIAN.get_record(robot).get_url()
        elif isinstance(source, RobotLibrarian):
            url = source.get_record(robot).get_url()
        elif isinstance(source, RobotRecord):
            url = source.get_url()
        elif isinstance(source, str):
            url = source
        else:
            raise TypeError("Invalid type for source: " + source)
        if position is None:
            position = {"x": 0, "y": 0, "z": 0}
        if rotation is None:
            rotation = {"x": 0, "y": 0, "z": 0}

        self._add_robot_command: dict = {"$type": "add_robot",
                                         "id": robot_id,
                                         "position": position,
                                         "rotation": rotation,
                                         "name": robot,
                                         "url": url}

    def get_initialization_commands(self) -> List[dict]:
        return [self._add_robot_command,
                {"$type": "send_static_robots",
                 "frequency": "once"},
                {"$type": "send_robots",
                 "frequency": "always"}]

    def on_send(self, resp: List[bytes]) -> None:
        # Initialize the static data.
        if self.static is None:
            self.static = RobotStatic(resp=resp, robot_id=self.robot_id)
        self.dynamic = RobotDynamic(resp=resp, robot_id=self.robot_id, previous=self.dynamic)

    def set_joint_targets(self, joints: Dict[int, Union[float, Dict[str, float]]]) -> None:
        """
        Set target angles or positions for a dictionary of joints.

        :param joints: A dictionary of joints to set. Key = The ID of the joint. Value = the targets. For spherical joints, this must be a Vector3 dictionary, for example `{"x": 40, "y": 0, "z": 0}`. For revolute and prismatic joints, this must be a float.
        """

        for joint_id in joints:
            joint_type = self.static.joints[joint_id].joint_type
            if joint_type == "fixed":
                continue
            elif joint_type == "spherical":
                assert isinstance(joints[joint_id], dict), f"Expected an x, y, z dictionary of targets for " \
                                                           f"{joint_id} but got {joints[joint_id]}"
                self.commands.append({"$type": "set_spherical_target",
                                      "target": joints[joint_id],
                                      "joint_id": joint_id,
                                      "id": self.robot_id})
            else:
                assert isinstance(joints[joint_id], float), f"Expected a float target for " \
                                                            f"{joint_id} but got {joints[joint_id]}"
                self.commands.append({"$type": "set_revolute_target" if joint_type == "revolute" else "set_prismatic_target",
                                      "target": float(joints[joint_id]),
                                      "joint_id": joint_id,
                                      "id": self.robot_id})

    def stop_joints(self, joint_ids: List[int] = None) -> None:
        """
        Stop the joints at their current angles or positions.

        :param joint_ids: A list of joint IDs. If None, stop all joints.
        """

        if joint_ids is None:
            joint_ids = self.static.joints.values()

        for joint_id in joint_ids:
            angles = self.dynamic.joints[joint_id].angles
            joint_type = self.static.joints[joint_id].joint_type
            if joint_type == "fixed":
                continue
            # Set the target to the angle of the first (and only) revolute drive.
            elif joint_type == "revolute":
                self.commands.append({"$type": "set_revolute_target",
                                      "joint_id": joint_id,
                                      "target": float(angles[0]),
                                      "id": self.robot_id})
            # Convert the current prismatic "angle" back into "radians".
            elif joint_type == "prismatic":
                self.commands.append({"$type": "set_prismatic_target",
                                      "joint_id": joint_id,
                                      "target": float(np.radians(angles[0])),
                                      "id": self.robot_id})
            # Set each spherical drive axis.
            else:
                self.commands.append({"$type": "set_spherical_target",
                                      "target": TDWUtils.array_to_vector3(angles),
                                      "joint_id": joint_id,
                                      "id": self.robot_id})

    def joints_are_moving(self, joint_ids: List[int] = None) -> bool:
        """
        :param joint_ids: A list of joint IDs to check for movement. If `None`, check all joints for movement.

        :return: True if the joints are moving.
        """

        if joint_ids is None:
            joint_ids = self.dynamic.joints.values()
        for joint_id in joint_ids:
            if self.dynamic.joints[joint_id].moving:
                return True
        return False
