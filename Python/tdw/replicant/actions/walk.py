from typing import List
from abc import ABC
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.actions.animate import Animate
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.collision_detection import CollisionDetection
from tdw.output_data import OutputData, Raycast
from tdw.tdw_utils import TDWUtils
from tdw.agents.arm import Arm
from tdw.agents.image_frequency import ImageFrequency
from tdw.controller import Controller


class Walk(Animate, ABC):
    """
    Abstract base class for walking motions.
    """

    _BOXCAST_Y: float = 0.25
    _BOXCAST_Z: float = 0.1
    _ANIMATION_NAME: str = "walking_02"

    def __init__(self, collision_detection: CollisionDetection, previous=None, reset_arms_num_frames: int = None):
        """
        :param collision_detection: The [`CollisionDetection`](collision_detection.md) rules.
        :param previous: The previous action. Can be None.
        :param reset_arms_num_frames: The number of frames for resetting the arms while walking. This controls the speed of the arm motion.
        """

        super().__init__(animation=Walk._ANIMATION_NAME,
                         collision_detection=collision_detection,
                         library="humanoid_animations.json",
                         previous=previous)
        self._reset_arms_num_frames: int = reset_arms_num_frames
        # Get the ID for the boxcast.
        self._boxcast_id: int = Controller.get_unique_id()

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        # Reset the arms.
        commands.extend([{"$type": "replicant_reset_arm",
                          "id": static.replicant_id,
                          "num_frames": self._reset_arms_num_frames,
                          "arm": arm.name} for arm in Arm])
        return commands

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        commands = super().get_ongoing_commands(resp=resp, static=static, dynamic=dynamic)
        if self.status != ActionStatus.ongoing:
            return commands
        if self._collision_detection.avoid:
            # Check the raycast data.
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                if r_id == "rayc":
                    raycast = Raycast(resp[i])
                    if raycast.get_raycast_id() == self._boxcast_id and raycast.get_hit() and raycast.get_hit_object():
                        if raycast.get_object_id() not in self._collision_detection.exclude_objects:
                            self.status = ActionStatus.detected_obstacle
                            return commands
            # Boxcast.
            position = dynamic.transform.position.copy()
            position[1] += Walk._BOXCAST_Y
            position[2] += Walk._BOXCAST_Z
            forward = dynamic.transform.forward.copy()
            forward[1] += Walk._BOXCAST_Y
            forward[2] += Walk._BOXCAST_Z
            commands.append({"$type": "send_boxcast",
                             "half_extents": {"x": 0.1, "y": 0.1, "z": 0.75},
                             "origin": TDWUtils.array_to_vector3(position),
                             "destination": TDWUtils.array_to_vector3(position + forward * 1.75),
                             "id": self._boxcast_id})
        return commands
