from typing import Optional
import numpy as np
from tdw.add_ons.audio_initializer_base import AudioInitializerBase
from tdw.tdw_utils import TDWUtils
from tdw.type_aliases import POSITION


class AudioInitializer(AudioInitializerBase):
    """
    Initialize standard (Unity) audio.

    This assumes that an avatar corresponding to `avatar_id` has already been added to the scene.
    """

    def __init__(self, avatar_id: str = "a", framerate: int = 30, physics_time_step: float = 0.02):
        """
        :param avatar_id: The ID of the listening avatar.
        :param framerate: The target simulation framerate.
        :param physics_time_step: The physics timestep.
        """

        super().__init__(avatar_id=avatar_id, framerate=framerate, physics_time_step=physics_time_step)

    def _get_sensor_command_name(self) -> str:
        return "add_audio_sensor"

    def _get_spatialization(self, position: Optional[POSITION]) -> dict:
        if position is None:
            return {"$type": "non_spatialized"}
        else:
            if isinstance(position, np.ndarray):
                pos = TDWUtils.array_to_vector3(position)
            elif isinstance(position, dict):
                pos = position
            else:
                raise Exception(f"Invalid position: {position}")
            return {"$type": "spatialized",
                    "position": pos}
