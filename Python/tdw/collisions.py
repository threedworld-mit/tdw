from typing import List, Dict
import numpy as np
from tdw.output_data import OutputData, Collision, EnvironmentCollision
from tdw.int_pair import IntPair


class CollisionObjObj:
    """
    A collision between two objects.
    """

    def __init__(self, collision: Collision):
        """
        :param collision: The collision output data.
        """

        """:field
        The contact point positions.
        """
        self.points: List[np.array] = list()
        """:field
        The contact point normals.
        """
        self.normals: List[np.array] = list()
        for i in range(collision.get_num_contacts()):
            self.points.append(np.array(collision.get_contact_point(i)))
            self.normals.append(np.array(collision.get_contact_normal(i)))
        """:field
        The relative velocity of the objects.
        """
        self.relative_velocity = np.array(collision.get_relative_velocity())


class CollisionObjEnv:
    """
    A collision between an object and the environment.
    """

    def __init__(self, collision: EnvironmentCollision):
        """
        :param collision: The collision output data.
        """

        """:field
        The contact point positions.
        """
        self.points: List[np.array] = list()
        """:field
        The contact point normals.
        """
        self.normals: List[np.array] = list()
        for i in range(collision.get_num_contacts()):
            self.points.append(np.array(collision.get_contact_point(i)))
            self.normals.append(np.array(collision.get_contact_normal(i)))


class Collisions:
    """
    A wrapper class for the output data of all collisions from a frame.

    """
    def __init__(self, resp: List[bytes]):
        """
        :param resp: The response from the build.
        """

        """:field
        All collisions between two objects that occurred on the frame.
        Key = The collision state: `"enter"`, `"stay"`, or `"exit"`.
        Value = A dictionary of collisions. Key = An `IntPair` (a pair of object IDs). Value = The collision.
        """
        self.obj_collisions: Dict[str, Dict[IntPair, CollisionObjObj]] = dict()
        """:field
        All collisions between an object and the environment that occurred on the frame.
        Key = The collision state: `"enter"`, `"stay"`, or `"exit"`.
        Value = A dictionary of collisions. Key = the object ID. Value = The collision.
        """
        self.env_collisions: Dict[str, Dict[int, CollisionObjEnv]] = dict()
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "coll":
                collision = Collision(resp[i])
                # Get the collision state.
                state = collision.get_state()
                if state not in self.obj_collisions:
                    self.obj_collisions[state] = dict()
                # Get the pair of IDs in this collision and use it as a key.
                ids = IntPair(int1=collision.get_collider_id(), int2=collision.get_collidee_id())
                coo = CollisionObjObj(collision=collision)
                self.obj_collisions[state][ids] = coo
            elif r_id == "enco":
                collision = EnvironmentCollision(resp[i])
                # Get the collision state.
                state = collision.get_state()
                if state not in self.env_collisions:
                    self.env_collisions[state] = dict()
                    coe = CollisionObjEnv(collision=collision)
                    self.env_collisions[state][collision.get_object_id()] = coe
