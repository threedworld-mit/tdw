from typing import Optional, List, Dict, Union
import numpy as np
from tdw.librarian import RobotLibrarian, RobotRecord
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.add_on import AddOn
from tdw.add_ons.robots.robot_static import RobotStatic
from tdw.add_ons.robots.robot_dynamic import RobotDynamic


class Robot(AddOn):
    """
    Add a robot to the scene and control its joints.

    ```python
    from tdw.controller import Controller
    from tdw.tdw_utils import TDWUtils
    from tdw.add_ons.robot import Robot
    from tdw.add_ons.third_person_camera import ThirdPersonCamera

    c = Controller(launch_build=False)
    c.start()
    # Create the robot add-on.
    robot_id = 0
    robot = Robot(name="ur5",
                  position={"x": 1, "y": 0, "z": -0.5},
                  robot_id=robot_id)
    # Create a camera add-on (for the purposes of seeing what's actually happening in this example).
    camera = ThirdPersonCamera(position={"x": -0.5, "y": 1, "z": 0},
                               look_at=robot_id)
    c.add_ons.extend([robot, camera])

    # Create an empty room (this will add the robot and the camera).
    c.communicate(TDWUtils.create_empty_room(12, 12))

    # Set target angles for the shoulder and forearm.
    targets = dict()
    for joint_id in robot.static.joints:
        name = robot.static.joints[joint_id].name
        if name == "shoulder_link":
            targets[joint_id] = 70
        elif name == "forearm_link":
            targets[joint_id] = -45
    robot.set_joint_targets(targets=targets)

    # Wait for the shoulder and forearm to stop moving.
    while robot.joints_are_moving():
        c.communicate([])

    # End the simulation.
    c.communicate({"$type": "terminate"})
    ```
    """

    """:class_var
    TDW's built-in [`RobotLibrarian`](../librarian/robot_librarian.md).
    """
    ROBOT_LIBRARIAN: RobotLibrarian = RobotLibrarian()
    """:class_var
    If a joint has moved less than this many degrees (revolute or spherical) or meters (prismatic) since the previous frame, it is considered to be not moving for the purposes of determining which joints are moving.
    """
    NON_MOVING: float = 0.001

    def __init__(self, name: str, position: Dict[str, float] = None, rotation: Dict[str, float] = None,
                 robot_id: int = 0, source: Union[RobotLibrarian, RobotRecord, str] = None):
        """
        :param name: The name of the robot.
        :param position: The position of the robot. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param rotation: The rotation of the robot in Euler angles (degrees). If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param robot_id: The ID of the robot.
        :param source: The source file of the robot. If None: The source will be the URL of the robot record in TDW's built-in [`RobotLibrarian`](../librarian/robot_librarian.md). If `str`: This is a filepath (starts with `file:///`) or a URL (starts with `http://` or `https://`). If `RobotRecord`: the source is the URL in the record. If `RobotLibrarian`: The source is the record in the provided `RobotLibrarian` that matches `name`.
        """

        super().__init__()
        """:field
        The ID of the robot.
        """
        self.robot_id: int = robot_id
        """:field
        [Static data](robots/robot_static.md) for this robot such as the IDs and masses of each joint.
        """
        self.static: Optional[RobotStatic] = None
        """:
        [Dynamic data](robots/robot_dynamic.md) for this robot such as the current position of the robot and current joint angles.
        """
        self.dynamic: Optional[RobotDynamic] = None

        url: str
        if source is None:
            url = Robot.ROBOT_LIBRARIAN.get_record(name).get_url()
        elif isinstance(source, RobotLibrarian):
            url = source.get_record(name).get_url()
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
                                         "name": name,
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
        dynamic = RobotDynamic(resp=resp, robot_id=self.robot_id, previous=self.dynamic)
        if self.dynamic is not None:
            # Check which joints are still moving.
            for joint_id in dynamic.joints:
                dynamic.joints[joint_id].moving = False
                for angle_0, angle_1 in zip(self.dynamic.joints[joint_id].angles, dynamic.joints[joint_id].angles):
                    if np.linalg.norm(angle_1 - angle_0) > Robot.NON_MOVING:
                        dynamic.joints[joint_id].moving = True
                        break
        else:
            for joint_id in dynamic.joints:
                dynamic.joints[joint_id].moving = True
        # Update the dynamic info.
        self.dynamic = dynamic

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
                self.commands.append(
                    {"$type": "set_revolute_target",
                     "target": float(targets[joint_id]),
                     "joint_id": joint_id,
                     "id": self.robot_id})
            elif joint_type == "prismatic":
                self.commands.append(
                    {"$type": "set_prismatic_target",
                     "target": float(targets[joint_id]),
                     "joint_id": joint_id,
                     "id": self.robot_id})
            else:
                raise Exception(f"Cannot set target for joint type {joint_type}")

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
            joint_ids = self.dynamic.joints.keys()
        for joint_id in joint_ids:
            if self.dynamic.joints[joint_id].moving:
                return True
        return False
