from enum import Enum
from typing import List
import numpy as np
from tdw.output_data import OutputData, Transforms
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.actions.action import Action
from tdw.replicant.replicant_simulation_state import CONTAINER_MANAGER
from tdw.agents.arm import Arm
from tdw.agents.image_frequency import ImageFrequency
from tdw.container_data.container_tag import ContainerTag


class _InitializationState(Enum):
    """
    State machine enum fails for initializing a drp[ action.
    """

    uninitialized = 0
    initialized_container_manager = 1
    initialize_drop = 2


class Drop(Action):
    """
    Drop a held object.
    """

    def __init__(self, arm: Arm, dynamic: ReplicantDynamic, max_num_frames: int = 100):
        """
        :param arm: The [`Arm`](../../agents/arm.md) holding the object.
        :param dynamic: The [`ReplicantDynamic`](../replicant_dynamic.md) data.
        :param max_num_frames: Wait this number of `communicate()` calls maximum for the object to stop moving before ending the action.
        """

        super().__init__()
        self._arm: Arm = arm
        if arm not in dynamic.held_objects:
            self.status = ActionStatus.not_holding
            self._object_id: int = 0
        else:
            self._object_id = dynamic.held_objects[arm]
        self._object_position: np.ndarray = np.zeros(shape=3)
        self._max_num_frames: int = max_num_frames
        self._frame_count: int = 0
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
            # Drop.
            commands.extend(self._get_drop_commands(resp=resp, static=static))
            # Get the initial position of the object.
            self._object_position = self._get_object_position(resp=resp)
            self._initialization_state = _InitializationState.initialize_drop
        return commands

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        if self._initialization_state == _InitializationState.initialized_container_manager:
            # Get the initial position of the object.
            self._object_position = self._get_object_position(resp=resp)
            self._initialization_state = _InitializationState.initialize_drop
            # Drop.
            return self._get_drop_commands(resp=resp, static=static)
        else:
            # Get the current position of the object.
            position = self._get_object_position(resp=resp)
            # The object stopped moving or fell through the floor.
            if np.linalg.norm(position - self._object_position) < 0.001 or position[1] < -0.1:
                self.status = ActionStatus.success
            else:
                # Update the current position.
                self._object_position = position
                self._frame_count += 1
                if self._frame_count >= self._max_num_frames:
                    self.status = ActionStatus.still_dropping
            return []

    def _get_object_position(self, resp: List[bytes]) -> np.ndarray:
        """
        :param resp: The response from the build.

        :return: The position of the held object.
        """

        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "tran":
                transforms = Transforms(resp[i])
                for j in range(transforms.get_num()):
                    if transforms.get_id(j) == self._object_id:
                        return transforms.get_position(j)
        raise Exception(f"Transform data not found for: {self._object_id}")

    def _get_drop_commands(self, resp: List[bytes], static: ReplicantStatic) -> List[dict]:
        """
        :param resp: The response from the build.
        :param static: The `ReplicantStatic` data.

        :return: A list of commands to unparent contained objects and drop the container.
        """

        # Update the container manager.
        CONTAINER_MANAGER.on_send(resp=resp)
        commands = []
        # Unparent all contained objects.
        for container_shape_id in CONTAINER_MANAGER.events:
            event = CONTAINER_MANAGER.events[container_shape_id]
            object_id = CONTAINER_MANAGER.container_shapes[container_shape_id]
            tag = CONTAINER_MANAGER.tags[container_shape_id]
            if object_id == self._object_id and tag == ContainerTag.inside:
                for ob_id in event.object_ids:
                    commands.extend([{"$type": "unparent_object",
                                      "id": int(ob_id)},
                                     {"$type": "set_kinematic_state",
                                      "id": int(ob_id),
                                      "is_kinematic": False,
                                      "use_gravity": True}])
        commands.append({"$type": "replicant_drop_object",
                         "id": static.replicant_id,
                         "arm": self._arm.name})
        return commands
