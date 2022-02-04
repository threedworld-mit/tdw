from typing import List, Tuple, Dict
from overrides import final
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, TriggerCollision
from tdw.add_ons.add_on import AddOn


class TriggerCollisionListener(AddOn):
    """
    Listen for trigger collisions between objects.
    """

    _NEXT_TRIGGER_ID: int = 0

    def __init__(self):
        """
        (no parameters)
        """

        super().__init__()
        """:field
        A dictionary of trigger colliders. Key = The object ID. Value = A list of trigger collider IDs.
        """
        self.trigger_colliders:  Dict[int, List[int]] = dict()
        """:field
        Trigger ID pairs describing trigger collisions on this frame.
        """
        self.trigger_collisions: List[Tuple[int, int]] = list()

    def get_initialization_commands(self) -> List[dict]:
        self.trigger_collisions.clear()
        self.trigger_colliders.clear()
        TriggerCollisionListener._NEXT_TRIGGER_ID = 0

        return []

    def on_send(self, resp: List[bytes]) -> None:
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "trco":
                trigger_collision = TriggerCollision(resp[i])
                # Get the IDs and form them into a tuple key.
                trigger_id = TriggerCollisionListener._get_trigger_id(trigger_collision.get_collider_id(),
                                                                      trigger_collision.get_collidee_id())
                # Begin a trigger collision.
                if trigger_collision.get_state() == "enter":
                    self.trigger_collisions.append(trigger_id)
                if trigger_collision.get_state() == "exit":
                    self.trigger_collisions.remove(trigger_id)

    @final
    def add_box_collider(self, object_id: int, position: Dict[str, float], scale: Dict[str, float],
                         rotation: Dict[str, float] = None, trigger_id: int = None) -> int:
        """
        Add a box-shaped trigger collider to an object.

        :param object_id: The ID of the object.
        :param position: The position of the trigger collider relative to the parent object.
        :param scale: The scale of the trigger collider.
        :param rotation: The rotation of the trigger collider in Euler angles relative to the parent object. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param trigger_id: The unique ID of the trigger collider. If None, an ID will be automatically assigned.

        :return: The ID of the trigger collider.
        """

        if rotation is None:
            rotation = TDWUtils.VECTOR3_ZERO
        trigger_id = self._add_trigger_collider(object_id=object_id, position=position, scale=scale, rotation=rotation,
                                                shape="cube", trigger_id=trigger_id)
        return trigger_id

    @final
    def add_sphere_collider(self, object_id: int, position: Dict[str, float], diameter: float,
                            trigger_id: int = None) -> int:
        """
        Add a sphere-shaped trigger collider to an object.

        :param object_id: The ID of the object.
        :param position: The position of the trigger collider relative to the parent object.
        :param diameter: The diameter of the trigger collider.
        :param trigger_id: The unique ID of the trigger collider. If None, an ID will be automatically assigned.

        :return: The ID of the trigger collider.
        """

        trigger_id = self._add_trigger_collider(object_id=object_id, position=position,
                                                scale={"x": diameter, "y": diameter, "z": diameter},
                                                rotation=TDWUtils.VECTOR3_ZERO,
                                                shape="sphere", trigger_id=trigger_id)
        return trigger_id

    def _add_trigger_collider(self, object_id: int, position: Dict[str, float], scale: Dict[str, float],
                              rotation: Dict[str, float], shape: str, trigger_id: int = None) -> int:
        """
        Add a trigger collider to an object.

        :param object_id: The ID of the object.
        :param position: The position of the trigger collider relative to the parent object.
        :param scale: The scale of the trigger collider.
        :param rotation: The rotation of the trigger collider in Euler angles relative to the parent object.
        :param shape: The shape of the collider. Options: "cube", "sphere".
        :param trigger_id: The unique ID of the trigger collider.
        """

        if object_id not in self.trigger_colliders:
            self.trigger_colliders[object_id] = list()
        assert trigger_id not in self.trigger_colliders[object_id], \
            f"Object {object_id} already has a trigger collider with ID {trigger_id}"
        if trigger_id is None:
            trigger_id = TriggerCollisionListener._NEXT_TRIGGER_ID
            TriggerCollisionListener._NEXT_TRIGGER_ID += 1
        self.commands.append({"$type": "add_trigger_collider",
                              "id": object_id,
                              "shape": shape,
                              "enter": True,
                              "stay": False,
                              "exit": True,
                              "trigger_id": trigger_id,
                              "scale": scale,
                              "position": position,
                              "rotation": rotation})
        self.trigger_colliders[object_id].append(trigger_id)
        return trigger_id

    @staticmethod
    def _get_trigger_id(a: int, b: int) -> Tuple[int, int]:
        if a < b:
            return a, b
        else:
            return b, a
