from tdw.container_data.container_tag import ContainerTag
from typing import List
import numpy as np
from tdw.replicant.actions.action import Action
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.replicant_simulation_state import CONTAINER_MANAGER, EMPTY_OBJECT_MANAGER
from tdw.agents.arm import Arm
from tdw.agents.image_frequency import ImageFrequency


class Grasp(Action):
    """
    Grasp a target object.
    """

    def __init__(self, target: int, arm: Arm, dynamic: ReplicantDynamic):
        """
        :param target: The target object ID.
        :param arm: The [`Arm`](../../agents/arm.md) value for the hand that will grasp the target object.
        :param dynamic: The [`ReplicantDynamic`](../replicant_dynamic.md) data.
        """

        super().__init__()
        self._target: int = target
        self._arm: Arm = arm
        # We're already holding an object.
        if self._arm in dynamic.held_objects:
            self.status = ActionStatus.already_holding

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        # Get all of the objects contained by the grasped object. Parent them to the container and make them kinematic.
        for container_shape_id in CONTAINER_MANAGER.events:
            event = CONTAINER_MANAGER.events[container_shape_id]
            object_id = CONTAINER_MANAGER.container_shapes[container_shape_id]
            tag = CONTAINER_MANAGER.tags[container_shape_id]
            if object_id == self._target and tag == ContainerTag.inside:
                for ob_id in event.object_ids:
                    commands.extend([{"$type": "parent_object_to_object",
                                      "parent_id": self._target,
                                      "id": int(ob_id)},
                                     {"$type": "set_kinematic_state",
                                      "id": int(ob_id),
                                      "is_kinematic": True,
                                      "use_gravity": False}])
        # Get the nearest empty object, if any.
        nearest_empty_object_distance: float = np.inf
        nearest_empty_object_id: int = 0
        got_empty_object: bool = False
        hand_position = dynamic.body_parts[static.hands[self._arm]].position
        for empty_object_id in EMPTY_OBJECT_MANAGER.empty_object_ids[self._target]:
            got_empty_object = True
            # Update the nearest affordance point.
            p = EMPTY_OBJECT_MANAGER.empty_object_positions[empty_object_id]
            d = np.linalg.norm(p - hand_position)
            # Too far away.
            if d > 0.99:
                continue
            if d < nearest_empty_object_distance:
                nearest_empty_object_distance = d
                nearest_empty_object_id = empty_object_id
        # Grasp the object.
        commands.append({"$type": "replicant_grasp_object",
                         "id": static.replicant_id,
                         "object_id": self._target,
                         "empty_object": got_empty_object,
                         "empty_object_id": nearest_empty_object_id})
        return commands

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        self.status = ActionStatus.success
        return []
