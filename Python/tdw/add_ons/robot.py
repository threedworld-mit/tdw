from typing import List, Dict, Union, Optional
from overrides import final
import numpy as np
from tdw.librarian import RobotLibrarian, RobotRecord
from tdw.tdw_utils import TDWUtils
from tdw.robot_data.robot_static import RobotStatic
from tdw.robot_data.robot_dynamic import RobotDynamic
from tdw.add_ons.robot_base import RobotBase


class Robot(RobotBase):
    """
    Add a robot to the scene and set joint targets and add joint forces. It has static and dynamic (per-frame) data for each of its joints.

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
    # Set joint targets.
    robot.set_joint_targets({robot.static.joint_ids_by_name["shoulder_link"]: 15,
                             robot.static.joint_ids_by_name["upper_arm_link"]: -45,
                             robot.static.joint_ids_by_name["forearm_link"]: 60})
    # Wait until the robot stops moving.
    while robot.joints_are_moving():
        c.communicate([])
    c.communicate({"$type": "terminate"})
    ```
    """

    """:class_var
    TDW's built-in [`RobotLibrarian`](../librarian/robot_librarian.md).
    """
    ROBOT_LIBRARIAN: RobotLibrarian = RobotLibrarian()

    def __init__(self, name: str, robot_id: int = 0, position: Dict[str, float] = None, rotation: Dict[str, float] = None,
                 source: Union[RobotLibrarian, RobotRecord, str] = None):
        """
        :param name: The name of the robot.
        :param robot_id: The ID of the robot.
        :param position: The position of the robot. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param rotation: The rotation of the robot in Euler angles (degrees). If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param source: The source file of the robot. If None: The source will be the URL of the robot record in TDW's built-in [`RobotLibrarian`](../librarian/robot_librarian.md). If `str`: This is a filepath (starts with `file:///`) or a URL (starts with `http://` or `https://`). If `RobotRecord`: the source is the URL in the record. If `RobotLibrarian`: The source is the record in the provided `RobotLibrarian` that matches `name`.
        """

        super().__init__(robot_id=robot_id, position=position, rotation=rotation)
        """:field
        [Static robot data.](../robot_data/robot_static.md)
        """
        self.static: Optional[RobotStatic] = None
        """:field
        [Dynamic robot data.](../robot_data/robot_dynamic.md)
        """
        self.dynamic: Optional[RobotDynamic] = None
        """:field
        The name of the robot.
        """
        self.name: str = name
        """:field
        The URL or filepath of the robot asset bundle.
        """
        self.url: str = ""
        if source is None:
            record: RobotRecord = Robot.ROBOT_LIBRARIAN.get_record(name)
            self.url = record.get_url()
        elif isinstance(source, RobotLibrarian):
            self.url = source.get_record(name).get_url()
        elif isinstance(source, RobotRecord):
            self.url = source.get_url()
        elif isinstance(source, str):
            self.url = source
        else:
            raise TypeError("Invalid type for source: " + source)

    def set_joint_targets(self, targets: Dict[int, Union[float, Dict[str, float]]]) -> None:
        """
        Set target angles or positions for a dictionary of joints.

        :param targets: A dictionary of joint targets. Key = The ID of the joint. Value = the targets. For spherical joints, this must be a Vector3 dictionary, for example `{"x": 40, "y": 0, "z": 0}` (angles in degrees). For revolute joints, this must be a float (an angle in degrees). For prismatic joints, this must be a float (a distance in meters).
        """

        for joint_id in targets:
            joint_type = self.static.joints[joint_id].joint_type
            if joint_type == "spherical":
                self.commands.append({"$type": "set_spherical_target",
                                      "target": targets[joint_id],
                                      "joint_id": joint_id,
                                      "id": self.robot_id})
            elif joint_type == "revolute":
                self.commands.append({"$type": "set_revolute_target",
                                      "target": float(targets[joint_id]),
                                      "joint_id": joint_id,
                                      "id": self.robot_id})
            elif joint_type == "prismatic":
                self.commands.append({"$type": "set_prismatic_target",
                                      "target": float(targets[joint_id]),
                                      "joint_id": joint_id,
                                      "id": self.robot_id})
            else:
                raise Exception(f"Cannot set target for joint type {joint_type}")
            self.dynamic.joints[joint_id].moving = True

    def add_joint_forces(self, forces: Dict[int, Union[float, Dict[str, float]]]) -> None:

        """
        Add torques and forces to a dictionary of joints.

        :param forces: A dictionary of joint forces. Key = The ID of the joint. Value = the targets. For spherical joints, this must be a Vector3 dictionary, for example `{"x": 40, "y": 0, "z": 0}` (torques in Newtons). For revolute joints, this must be a float (a torque in Newtons). For prismatic joints, this must be a float (a force in Newtons).
        """

        for joint_id in forces:
            joint_type = self.static.joints[joint_id].joint_type
            if joint_type == "spherical":
                self.commands.append({"$type": "add_torque_to_spherical",
                                      "torque": forces[joint_id],
                                      "joint_id": joint_id,
                                      "id": self.robot_id})
            elif joint_type == "revolute":
                self.commands.append({"$type": "add_torque_to_revolute",
                                      "torque": float(forces[joint_id]),
                                      "joint_id": joint_id,
                                      "id": self.robot_id})
            elif joint_type == "prismatic":
                self.commands.append({"$type": "add_force_to_prismatic",
                                      "force": float(forces[joint_id]),
                                      "joint_id": joint_id,
                                      "id": self.robot_id})
            else:
                raise Exception(f"Cannot apply torque or force to joint type {joint_type}")
            self.dynamic.joints[joint_id].moving = True

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

    @final
    def _get_add_robot_command(self) -> dict:
        return {"$type": "add_robot",
                "id": self.robot_id,
                "position": self.initial_position,
                "rotation": self.initial_rotation,
                "name": self.name,
                "url": self.url}

    def _cache_static_data(self, resp: List[bytes]) -> None:
        self.static = RobotStatic(robot_id=self.robot_id, resp=resp)

    def _set_dynamic_data(self, resp: List[bytes]) -> None:
        dynamic = RobotDynamic(resp=resp, robot_id=self.robot_id, body_parts=self.static.body_parts,
                               previous=self.dynamic)
        self.dynamic = self._set_joints_moving(dynamic)
