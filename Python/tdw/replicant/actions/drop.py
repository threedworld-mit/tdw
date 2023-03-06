from typing import List
import numpy as np
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.actions.action import Action
from tdw.replicant.arm import Arm
from tdw.replicant.image_frequency import ImageFrequency


class Drop(Action):
    """
    Drop a held object.

    The action ends when the object stops moving or the number of consecutive `communicate()` calls since dropping the object exceeds `self.max_num_frames`.

    When an object is dropped, it is made non-kinematic. Any objects contained by the object are parented to it and also made non-kinematic. For more information regarding containment in TDW, [read this](../../../lessons/semantic_states/containment.md).
    """

    def __init__(self, arm: Arm, dynamic: ReplicantDynamic, max_num_frames: int):
        """
        :param arm: The [`Arm`](../arm.md) holding the object.
        :param dynamic: The [`ReplicantDynamic`](../replicant_dynamic.md) data that changes per `communicate()` call.
        :param max_num_frames: Wait this number of `communicate()` calls maximum for the object to stop moving before ending the action.
        """

        super().__init__()
        """:field
        The [`Arm`](../arm.md) holding the object.
        """
        self.arm: Arm = arm
        if arm not in dynamic.held_objects:
            self.status = ActionStatus.not_holding
            """:field
            The ID of the held object.
            """
            self.object_id: int = 0
        else:
            self.object_id = dynamic.held_objects[arm]
        """:field
        The current position of the object.
        """
        self.object_position: np.ndarray = np.zeros(shape=3)
        """:field
        Wait this number of `communicate()` calls maximum for the object to stop moving before ending the action.
        """
        self.max_num_frames: int = max_num_frames
        """:field
        The current frame.
        """
        self.frame_count: int = 0
        self._first_frame: bool = True

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        commands.extend([{"$type": "replicant_drop_object",
                          "id": static.replicant_id,
                          "arm": self.arm.name},
                         {"$type": "enable_nav_mesh_obstacle",
                          "id": self.object_id,
                          "enable": True}])
        self.object_position = self._get_object_position(object_id=self.object_id, resp=resp)
        return commands

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        # The build might've signaled that the action ended in failure.
        if dynamic.output_data_status != ActionStatus.ongoing or self._first_frame:
            self._first_frame = False
            self.status = dynamic.output_data_status
            return []
        position = self._get_object_position(object_id=self.object_id, resp=resp)
        # The object stopped moving or fell through the floor.
        if np.linalg.norm(position - self.object_position) < 0.001 or position[1] < -0.1:
            self.status = ActionStatus.success
        else:
            # Update the current position.
            self.object_position = position
            self.frame_count += 1
            if self.frame_count >= self.max_num_frames:
                self.status = ActionStatus.still_dropping
        return super().get_ongoing_commands(resp=resp, static=static, dynamic=dynamic)
