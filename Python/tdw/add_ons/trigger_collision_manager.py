from typing import List, Dict
from overrides import final
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData
from tdw.output_data import TriggerCollision as Trigger
from tdw.collision_data.trigger_collision import TriggerCollision
from tdw.add_ons.add_on import AddOn


class TriggerCollisionManager(AddOn):
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
        A dictionary of trigger colliders. Key = The trigger ID. Value = The object ID.
        """
        self.trigger_ids:  Dict[int, int] = dict()
        """:field
        A list of [`TriggerCollision`](../collision_data/trigger_collision.md) events from this frame.
        """
        self.collisions: List[TriggerCollision] = list()

    def get_initialization_commands(self) -> List[dict]:
        return []

    def on_send(self, resp: List[bytes]) -> None:
        self.collisions.clear()
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "trco":
                self.collisions.append(TriggerCollision(Trigger(resp[i])))

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

    @final
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

        assert trigger_id not in self.trigger_ids, f"Trigger {trigger_id} already exists."
        if trigger_id is None:
            trigger_id = TriggerCollisionManager._NEXT_TRIGGER_ID
            TriggerCollisionManager._NEXT_TRIGGER_ID += 1
        self.commands.append({"$type": "add_trigger_collider",
                              "id": object_id,
                              "shape": shape,
                              "enter": True,
                              "stay": True,
                              "exit": True,
                              "trigger_id": trigger_id,
                              "scale": scale,
                              "position": position,
                              "rotation": rotation})
        self.trigger_ids[trigger_id] = object_id
        return trigger_id

    def reset(self) -> None:
        """
        Reset this add-on. Call this before resetting a scene.
        """

        self.collisions.clear()
        self.trigger_ids.clear()
        TriggerCollisionManager._NEXT_TRIGGER_ID = 0
