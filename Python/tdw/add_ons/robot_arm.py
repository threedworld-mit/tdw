from typing import List, Dict, Union
import numpy as np
from overrides import final
from ikpy.chain import Chain
from ikpy.link import OriginLink, URDFLink, Link
from tdw.tdw_utils import TDWUtils
from tdw.quaternion_utils import QuaternionUtils
from tdw.add_ons.robot import Robot
from tdw.librarian import RobotLibrarian, RobotRecord


class RobotArm(Robot):
    """
    A robot with a single arm.
    This class includes an inverse kinematic (IK) solver that allows the robot to reach for a target position.
    """

    def __init__(self, name: str, robot_id: int = 0, position: Dict[str, float] = None, rotation: Dict[str, float] = None,
                 source: Union[RobotLibrarian, RobotRecord] = None):
        """
        :param name: The name of the robot.
        :param robot_id: The ID of the robot.
        :param position: The position of the robot. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param rotation: The rotation of the robot in Euler angles (degrees). If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param source: The source file of the robot. If None: The source will be the URL of the robot record in TDW's built-in [`RobotLibrarian`](../librarian/robot_librarian.md). If `RobotRecord`: the source is the URL in the record. If `RobotLibrarian`: The source is the record in the provided `RobotLibrarian` that matches `name`.
        """

        super().__init__(name=name, robot_id=robot_id, position=position, rotation=rotation, source=source)
        assert self._record is not None, "Record is None."
        assert len(self._record.ik) > 0, "Record doesn't have IK data."
        # A list of joint names in the order that they appear in the IK chain.
        self._joint_order: List[str] = list()
        # Convert the record data into joint links.
        links: List[Link] = [OriginLink()]
        for link in self._record.ik[0]:
            self._joint_order.append(link["name"])
            links.append(URDFLink(name=link["name"],
                                  translation_vector=np.array(link["translation_vector"]),
                                  orientation=np.array(link["orientation"]),
                                  rotation=None if link["rotation"] is None else np.array(link["rotation"]),
                                  bounds=link["bounds"]))
        # Set robot arm IK chain.
        self._chain: Chain = Chain(name=name, links=links)

    def reach_for(self, target: Union[Dict[str, float], np.array]) -> None:
        """
        Start to reach for a target position.

        :param target: The target position. Can be a dictionary or a numpy array.
        """

        angles = self._get_ik_angles(target=target)
        # Convert the IK solution to degrees. Remove the origin link.
        angles = [float(np.rad2deg(angle)) for angle in angles[1:]]
        # Convert the angles to a dictionary of joint targets.
        targets = dict()
        for joint_name, angle in zip(self._joint_order, angles):
            targets[self.static.joint_ids_by_name[joint_name]] = angle
        self.set_joint_targets(targets=targets)

    def set_joint_targets(self, targets: Dict[int, Union[float, Dict[str, float]]]) -> None:
        """
        Set target angles or positions for a dictionary of joints.

        :param targets: A dictionary of joint targets. Key = The ID of the joint. Value = the targets. For spherical joints, this must be a Vector3 dictionary, for example `{"x": 40, "y": 0, "z": 0}` (angles in degrees). For revolute joints, this must be a float (an angle in degrees). For prismatic joints, this must be a float (a distance in meters).
        """

        super().set_joint_targets(targets=targets)

    def add_joint_forces(self, forces: Dict[int, Union[float, Dict[str, float]]]) -> None:
        """
        Add torques and forces to a dictionary of joints.

        :param forces: A dictionary of joint forces. Key = The ID of the joint. Value = the targets. For spherical joints, this must be a Vector3 dictionary, for example `{"x": 40, "y": 0, "z": 0}` (torques in Newtons). For revolute joints, this must be a float (a torque in Newtons). For prismatic joints, this must be a float (a force in Newtons).
        """

        super().add_joint_forces(forces=forces)

    def stop_joints(self, joint_ids: List[int] = None) -> None:
        """
        Stop the joints at their current angles or positions.

        :param joint_ids: A list of joint IDs. If None, stop all joints.
        """

        super().stop_joints(joint_ids=joint_ids)

    @final
    def _get_ik_angles(self, target: Union[Dict[str, float], np.array]) -> List[float]:
        """
        :param target: The target position to reach for.

        :return: A list of angles of an IK solution in radians.
        """

        # Get the current angles of the joints.
        initial_angles = [0]
        for joint_name in self._joint_order:
            initial_angles.append(self.dynamic.joints[self.static.joint_ids_by_name[joint_name]].angles[0])
        initial_angles = np.radians(initial_angles)
        if isinstance(target, dict):
            target = TDWUtils.vector3_to_array(target)
        # Convert the worldspace position to a relative position.
        relative_target = self._absolute_to_relative(target=target)
        # Get the IK solution.
        return self._chain.inverse_kinematics(target_position=relative_target, initial_position=initial_angles)

    @final
    def _absolute_to_relative(self, target: np.array) -> np.array:
        """
        :param target: The target position.
        :return: The target position in relative coordinates.
        """

        return QuaternionUtils.world_to_local_vector(position=target,
                                                     origin=self.dynamic.transform.position,
                                                     rotation=self.dynamic.transform.rotation)
