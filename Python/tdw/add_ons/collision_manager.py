from typing import Dict, List
from tdw.output_data import OutputData, Collision, EnvironmentCollision
from tdw.collision_data.collision_obj_obj import CollisionObjObj
from tdw.collision_data.collision_obj_env import CollisionObjEnv
from tdw.int_pair import IntPair
from tdw.add_ons.add_on import AddOn


class CollisionManager(AddOn):
    """
    Manager add-on for all collisions on this frame.
    """
    
    def __init__(self, enter: bool = True, stay: bool = False, exit: bool = False,
                 objects: bool = True, environment: bool = True):
        """
        :param enter: If True, listen for collision enter events.
        :param stay: If True, listen for collision stay events.
        :param exit: If True, listen for collision exit events.
        :param objects: If True, listen for collisions between objects.
        :param environment: If True, listen for collisions between an object and the environment.
        """

        super().__init__()
        collision_types: List[str] = list()
        if objects:
            collision_types.append("obj")
        if environment:
            collision_types.append("env")
        self._send_collision_commands: dict = {"$type": "send_collisions",
                                               "enter": enter,
                                               "stay": stay,
                                               "exit": exit,
                                               "collision_types": collision_types}
        """:field
        All collisions between two objects that occurred on the frame.
        Key = An `IntPair` (a pair of object IDs). Value = [The collision.](../collision_data/collision_obj_obj.md)
        """
        self.obj_collisions: Dict[IntPair, CollisionObjObj] = dict()
        """:field
        All collisions between an object and the environment that occurred on the frame.
        Key = the object ID. Value = [The collision.](../collision_data/collision_obj_env.md)
        """
        self.env_collisions: Dict[int, CollisionObjEnv] = dict()

    def get_initialization_commands(self) -> List[dict]:
        return [self._send_collision_commands]

    def on_send(self, resp: List[bytes]) -> None:
        self.obj_collisions.clear()
        self.env_collisions.clear()
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "coll":
                collision = Collision(resp[i])
                # Get the pair of IDs in this collision and use it as a key.
                ids = IntPair(int1=collision.get_collider_id(), int2=collision.get_collidee_id())
                coo = CollisionObjObj(collision=collision)
                self.obj_collisions[ids] = coo
            elif r_id == "enco":
                collision = EnvironmentCollision(resp[i])
                coe = CollisionObjEnv(collision=collision)
                self.env_collisions[collision.get_object_id()] = coe
