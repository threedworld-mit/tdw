from typing import List, Dict, Optional, Tuple
import numpy as np
from tdw.output_data import OutputData, Robot, Collision, EnvironmentCollision
from tdw.object_data.transform import Transform
from tdw.robot_data.joint_dynamic import JointDynamic
from tdw.collision_data.collision_obj_obj import CollisionObjObj
from tdw.collision_data.collision_obj_env import CollisionObjEnv


class RobotDynamic:
    """
    Dynamic data for a robot that can change per frame (such as the position of the robot, the angle of a joint, etc.)
    """

    """:class_var
    If the joint moved by less than this angle or distance since the previous frame, it's considered to be non-moving.
    """
    NON_MOVING: float = 0.001

    def __init__(self, robot_id: int, resp: List[bytes], body_parts: List[int], previous=None):
        """
        :param resp: The response from the build, which we assume contains `Robot` output data.
        :param robot_id: The ID of this robot.
        :param body_parts: The IDs of all body parts belonging to this robot.
        :param previous: If not None, the previous RobotDynamic data. Use this to determine if the joints are moving.
        """

        """:field
        The Transform data for this robot.
        """
        self.transform: Optional[Transform] = None
        """:field
        A dictionary of [dynamic joint data](joint_dynamic.md). Key = The ID of the joint.
        """
        self.joints: Dict[int, JointDynamic] = dict()
        """:field
        If True, this robot is immovable.
        """
        self.immovable: bool = False
        """:field
        A dictionary of collisions between one of this robot's [body parts (joints or non-moving)](robot_static.md) and another object.
        Key = A tuple where the first element is the body part ID and the second element is the object ID.
        Value = A list of [collision data.](../collision_data/collision_obj_obj.md)
        """
        self.collisions_with_objects: Dict[Tuple[int, int], List[CollisionObjObj]] = dict()
        """:field
        A dictionary of collisions between two of this robot's [body parts](robot_static.md).
        Key = An unordered tuple of two body part IDs.
        Value = A list of [collision data.](../collision_data/collision_obj_obj.md)
        """
        self.collisions_with_self: Dict[Tuple[int, int], List[CollisionObjObj]] = dict()
        """:field
        A dictionary of collisions between one of this robot's [body parts](robot_static.md) and the environment (floors, walls, etc.).
        Key = The ID of the body part.
        Value = A list of [environment collision data.](../collision_data/collision_obj_env.md)
        """
        self.collisions_with_environment: Dict[int, List[CollisionObjEnv]] = dict()
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "robo":
                robot: Robot = Robot(resp[i])
                if robot.get_id() == robot_id:
                    self.transform = Transform(position=np.array(robot.get_position()),
                                               rotation=np.array(robot.get_rotation()),
                                               forward=np.array(robot.get_forward()))
                    self.immovable = robot.get_immovable()
                    # Get dynamic data for each joint.
                    for j in range(robot.get_num_joints()):
                        joint = JointDynamic(robot=robot, joint_index=j)
                        # Determine if the joint is currently moving.
                        if previous is not None:
                            previous: RobotDynamic
                            previous_joint: JointDynamic = previous.joints[joint.joint_id]
                            for k in range(len(previous_joint.angles)):
                                if np.linalg.norm(previous_joint.angles[k] - joint.angles[k]) > RobotDynamic.NON_MOVING:
                                    joint.moving = True
                                    break
                        self.joints[joint.joint_id] = joint
            # Record collisions between myself and my joints or with another object.
            elif r_id == "coll":
                collision = Collision(resp[i])
                collider_id: int = collision.get_collider_id()
                collidee_id: int = collision.get_collidee_id()
                # Record collisions between one of my body parts and another of my body parts.
                if collider_id in body_parts and collidee_id in body_parts:
                    key: Tuple[int, int] = (collider_id, collidee_id)
                    c = CollisionObjObj(collision)
                    # Record this collision.
                    if key not in self.collisions_with_self:
                        self.collisions_with_self[key] = [c]
                    else:
                        self.collisions_with_self[key].append(c)
                # Record collisions between one of my body parts and another object.
                elif collider_id in body_parts or collidee_id in body_parts:
                    # The body part is the first element in the tuple.
                    if collider_id in body_parts:
                        key: Tuple[int, int] = (collider_id, collidee_id)
                    else:
                        key: Tuple[int, int] = (collidee_id, collider_id)
                    # Record this collision.
                    c = CollisionObjObj(collision)
                    if key not in self.collisions_with_self:
                        self.collisions_with_objects[key] = [c]
                    else:
                        self.collisions_with_objects[key].append(c)
            elif r_id == "enco":
                collision = EnvironmentCollision(resp[i])
                object_id = collision.get_object_id()
                if object_id in body_parts:
                    c = CollisionObjEnv(collision)
                    if object_id not in self.collisions_with_environment:
                        self.collisions_with_environment[object_id] = [c]
                    else:
                        self.collisions_with_environment[object_id].append(c)
