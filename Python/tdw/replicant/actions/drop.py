from typing import List
import numpy as np
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.actions.action import Action
from tdw.agents.arm import Arm
from tdw.agents.image_frequency import ImageFrequency
from tdw.output_data import OutputData, Transforms, Containment


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

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        # Unparent all contained objects.
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "cont":
                containment = Containment(resp[i])
                object_id = containment.get_object_id()
                if object_id == self._object_id:
                    overlap_ids = containment.get_overlap_ids()
                    for overlap_id in overlap_ids:
                        commands.extend([{"$type": "unparent_object",
                                          "id": int(overlap_id)},
                                         {"$type": "set_kinematic_state",
                                          "id": int(overlap_id),
                                          "is_kinematic": False,
                                          "use_gravity": True}])
        commands.append({"$type": "replicant_drop_object",
                         "id": static.replicant_id,
                         "arm": self._arm.name})
        self._object_position = self._get_object_position(resp=resp)
        return commands

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
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

    def _get_object_position(self, resp: List[bytes]):
        """
        :param resp: The response from the build.

        :return: The position of the target object.
        """

        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "tran":
                transforms = Transforms(resp[i])
                for j in range(transforms.get_num()):
                    if transforms.get_id(j) == self._object_id:
                        return transforms.get_position(j)
                    break
                break
        raise Exception(f"No transform data found for: {self._object_id}")
