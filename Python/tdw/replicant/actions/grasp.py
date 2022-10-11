from enum import Enum
from tdw.container_data.container_tag import ContainerTag
from typing import List
from tdw.output_data import OutputData, EmptyObjects
import numpy as np
from tdw.replicant.actions.action import Action
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.replicant_simulation_state import CONTAINER_MANAGER
from tdw.agents.arm import Arm
from tdw.agents.image_frequency import ImageFrequency


class _InitializationState(Enum):
    """
    State machine enum fails for initializing a grasp action.
    """

    uninitialized = 0
    initialized_container_manager = 1
    initialized_grasp = 2


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
        # Set the initialization state.
        if CONTAINER_MANAGER.initialized:
            self._initialization_state: _InitializationState = _InitializationState.initialized_container_manager
        else:
            self._initialization_state = _InitializationState.uninitialized

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        # Initialize the container manager.
        if self._initialization_state == _InitializationState.uninitialized:
            commands.extend(CONTAINER_MANAGER.get_initialization_commands())
            CONTAINER_MANAGER.initialized = True
            self._initialization_state = _InitializationState.initialized_container_manager
        elif self._initialization_state == _InitializationState.initialized_container_manager:
            commands.extend(self._get_grasp_commands(resp=resp, static=static, dynamic=dynamic))
            self._initialization_state = _InitializationState.initialized_grasp
        return commands

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        # We grasped the object.
        if self._initialization_state == _InitializationState.initialized_grasp:
            self.status = ActionStatus.success
            return []
        else:
            self._initialization_state = _InitializationState.initialized_grasp
            return self._get_grasp_commands(resp=resp, static=static, dynamic=dynamic)

    def _get_grasp_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        # Update the container manager.
        CONTAINER_MANAGER.on_send(resp=resp)
        commands = []
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
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            # Get the empty objects.
            if r_id == "empt":
                empty_objects = EmptyObjects(resp[i])
                for j in range(empty_objects.get_num()):
                    empty_object_id = empty_objects.get_id(j)
                    if empty_object_id == self._target:
                        got_empty_object = True
                        # Update the nearest affordance point.
                        p = empty_objects.get_position(j)
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
