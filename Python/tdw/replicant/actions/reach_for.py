from typing import List, Dict, Union
import numpy as np
from tdw.output_data import OutputData, EmptyObjects, Bounds
from tdw.tdw_utils import TDWUtils
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.actions.action import Action
from tdw.agents.image_frequency import ImageFrequency
from tdw.agents.arm import Arm


class ReachFor(Action):
    """
    Reach for a target object or position.
    """

    def __init__(self, target: Union[int, np.ndarray, Dict[str,  float]], arms: List[Arm], num_frames: int = 15):
        """
        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param arms: The [`Arm`](../../agents/arm.md) values that will reach for the `target`. Example: `[Arm.left, Arm.right]`.
        :param num_frames: The number of frames for the action. This controls the speed of the action.
        """

        super().__init__()
        self._arms: List[Arm] = arms
        self._frame_count: int = 0
        self._target: Union[int, np.ndarray, Dict[str,  float]] = target
        self._initialized: bool = False
        self._num_frames: int = num_frames

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        # Request Bounds data.
        commands.extend([{"$type": "send_bounds",
                          "frequency": "once"}])
        return commands

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        if not self._initialized:
            self._initialized = True
            targets: Dict[Arm, Dict[str, float]] = dict()
            # Reach for a target position.
            if isinstance(self._target, np.ndarray):
                targets = {arm: TDWUtils.array_to_vector3(self._target) for arm in self._arms}
            elif isinstance(self._target, dict):
                targets = {arm: self._target for arm in self._arms}
            # Reach for a target object.
            elif isinstance(self._target, int):
                centroid: np.ndarray = np.zeros(shape=3)
                nearest_empty_object_distances: Dict[Arm, float] = dict()
                nearest_empty_object_positions: Dict[Arm, np.ndarray] = dict()
                hand_positions = {arm: dynamic.body_parts[static.hands[arm]] for arm in self._arms}
                for i in range(len(resp) - 1):
                    r_id = OutputData.get_data_type_id(resp[i])
                    # Get the centroid of the object.
                    if r_id == "boun":
                        bounds = Bounds(resp[i])
                        for j in range(bounds.get_num()):
                            if bounds.get_id(j) == self._target:
                                centroid = bounds.get_center(j)
                                break
                    # Get the empty objects.
                    elif r_id == "empt":
                        empty_objects = EmptyObjects(resp[i])
                        for j in range(empty_objects.get_num()):
                            if empty_objects.get_id(j) == self._target:
                                # Update the nearest affordance point per arm.
                                for arm in self._arms:
                                    p = empty_objects.get_position(j)
                                    d = np.linalg.norm(p - hand_positions[arm])
                                    # Too far away.
                                    if d > 0.99:
                                        continue
                                    if d < nearest_empty_object_distances[arm]:
                                        nearest_empty_object_distances[arm] = d
                                        nearest_empty_object_positions[arm] = p
                # Reach for an affordance point.
                for arm in self._arms:
                    if arm in nearest_empty_object_positions:
                        targets[arm] = TDWUtils.array_to_vector3(nearest_empty_object_positions[arm])
                    else:
                        d = np.linalg.norm(centroid - hand_positions[arm])
                        # The centroid is close enough.
                        if d < 0.99:
                            targets[arm] = TDWUtils.array_to_vector3(centroid)
            else:
                raise Exception(f"Invalid target: {self._target}")
            # Immediately fail because one or both arms can't reach a target.
            for arm in self._arms:
                if arm not in targets:
                    self.status = ActionStatus.cannot_reach
                    return []
            # Reach for the target.
            return [{"$type": "replicant_reach_for_position",
                     "position": targets[arm],
                     "id": static.replicant_id,
                     "num_frames": self._num_frames,
                     "arm": arm} for arm in self._arms]
        self._frame_count += 1
        if self._frame_count >= self._num_frames:
            self.status = ActionStatus.success
        return []
