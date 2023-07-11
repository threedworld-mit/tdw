from typing import List, Union, Dict
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Replicants, Containment
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

    def __init__(self, arm: Arm, dynamic: ReplicantDynamic, max_num_frames: int, offset: Union[float, np.ndarray, Dict[str, float]]):
        """
        :param arm: The [`Arm`](../arm.md) holding the object.
        :param dynamic: The [`ReplicantDynamic`](../replicant_dynamic.md) data that changes per `communicate()` call.
        :param max_num_frames: Wait this number of `communicate()` calls maximum for the object to stop moving before ending the action.
        :param offset: Prior to being dropped, set the object's positional offset. This can be a float (a distance along the object's forward directional vector). Or it can be a dictionary or numpy array (a world space position).
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
        """:field
        Prior to being dropped, set the object's positional offset. This can be a float (a distance along the object's forward directional vector). Or it can be a dictionary or numpy array (a world space position).
        """
        self.offset: Union[float, np.ndarray, Dict[str, float]] = offset
        self._first_frame: bool = True

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        # Get the offset distance from the hand.
        if isinstance(self.offset, float):
            offset_distance = self.offset
        else:
            offset_distance = 0
        # Drop the object and enable its NavMeshObstacle if it has one.
        commands.extend([{"$type": "replicant_drop_object",
                          "id": static.replicant_id,
                          "arm": self.arm.name,
                          "offset_distance": offset_distance},
                         {"$type": "enable_nav_mesh_obstacle",
                          "id": self.object_id,
                          "enable": True}])
        # Possible teleport the object.
        if isinstance(self.offset, dict):
            commands.append({"$type": "teleport_object",
                             "id": self.object_id,
                             "position": self.offset})
        elif isinstance(self.offset, np.ndarray):
            commands.append({"$type": "teleport_object",
                             "id": self.object_id,
                             "position": TDWUtils.array_to_vector3(self.offset)})
        # Stop ignoring collisions with the held object.
        commands.append({"$type": "ignore_collisions",
                         "id": self.object_id,
                         "other_id": static.replicant_id,
                         "ignore": False})
        # Stop ignoring collisions with the contained objects.
        replicant_ids: List[int] = list()
        # Get all Replicant IDs.
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "repl":
                replicants = Replicants(resp[i])
                for j in range(replicants.get_num()):
                    replicant_ids.append(replicants.get_id(j))
                break
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "cont":
                containment = Containment(resp[i])
                object_id = containment.get_object_id()
                if object_id == self.object_id:
                    overlap_ids = containment.get_overlap_ids()
                    # Ignore Replicants.
                    overlap_ids = [o_id for o_id in overlap_ids if o_id not in replicant_ids]
                    for overlap_id in overlap_ids:
                        child_id = int(overlap_id)
                        commands.append({"$type": "ignore_collisions",
                                         "id": child_id,
                                         "other_id": static.replicant_id,
                                         "ignore": False})
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
