from typing import List, Dict, Tuple
import numpy as np
from tdw.output_data import OutputData, Collision, EnvironmentCollision, DynamicRobots
from tdw.object_data.transform import Transform
from tdw.robot_data.robot_static import RobotStatic
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

    def __init__(self, static: RobotStatic, resp: List[bytes]):
        """
        :param static: [`RobotStatic`](robot_static.md) data for this robot.
        :param resp: The response from the build.
        """

        """:field
        The [`Transform`](../object_data/transform.md) data for this robot.
        """
        self.transform: Transform = Transform(position=np.array([0, 0, 0]),
                                              rotation=np.array([0, 0, 0, 0]),
                                              forward=np.array([0, 0, 0]))
        """:field
        A dictionary of [`JointDynamic`](joint_dynamic.md). Key = The ID of the joint.
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
            # Record collisions between myself and my joints or with another object.
            if r_id == "drob":
                dynamic_robots = DynamicRobots(resp[i])
                self.immovable = dynamic_robots.get_immovable(static.robot_index)
                self.transform = Transform(position=dynamic_robots.get_robot_position(static.robot_index),
                                           rotation=dynamic_robots.get_robot_rotation(static.robot_index),
                                           forward=dynamic_robots.get_robot_forward(static.robot_index))
                for joint_id in static.joints:
                    joint_index = static.joints[joint_id].dynamic_index
                    self.joints[joint_id] = JointDynamic(joint_id=joint_id,
                                                         position=dynamic_robots.get_joint_position(index=joint_index),
                                                         angles=dynamic_robots.get_joint_angles(index=joint_index)[:static.joints[joint_id].num_dof],
                                                         moving=False)
            elif r_id == "coll":
                collision = Collision(resp[i])
                collider_id: int = collision.get_collider_id()
                collidee_id: int = collision.get_collidee_id()
                # Record collisions between one of my body parts and another of my body parts.
                if collider_id in static.body_parts and collidee_id in static.body_parts:
                    key: Tuple[int, int] = (collider_id, collidee_id)
                    c = CollisionObjObj(collision)
                    # Record this collision.
                    if key not in self.collisions_with_self:
                        self.collisions_with_self[key] = [c]
                    else:
                        self.collisions_with_self[key].append(c)
                # Record collisions between one of my body parts and another object.
                elif collider_id in static.body_parts or collidee_id in static.body_parts:
                    # The body part is the first element in the tuple.
                    if collider_id in static.body_parts:
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
                if object_id in static.body_parts:
                    c = CollisionObjEnv(collision)
                    if object_id not in self.collisions_with_environment:
                        self.collisions_with_environment[object_id] = [c]
                    else:
                        self.collisions_with_environment[object_id].append(c)
