from typing import Optional
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller
from tdw.add_ons.audio_initializer_base import AudioInitializerBase
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

    def play_from_streaming_assets(self, path: str, position: Optional[POSITION], audio_id: int = None,
                                   object_id: int = None, loop: bool = False) -> None:
        """
        Load a .wav file from the `StreamingAssets/` directory in the build and prepare to send a command to the build to play the audio.
        The command will be sent on the next `Controller.communicate()` call.

        To find `StreamingAssets/`, [read this](https://docs.unity3d.com/Manual/StreamingAssets.html).

        :param path: The path to a .wav file relative to StreamingAssets, for example `audio/example_sound.wav`.
        :param position: The position of audio source. Can be a numpy array or x, y, z dictionary. If None, the sound won't be spatialized.
        :param audio_id: The unique ID of the audio source. If None, a random ID is generated.
        :param object_id: If not None, parent the audio source to this object. Ignored if `position` is None.
        :param loop: If True, the audio will loop.
        """

        if position is None:
            spatialize = False
            pos = {"x": 0, "y": 0, "z": 0}
        else:
            spatialize = True
            if isinstance(position, np.ndarray):
                pos = TDWUtils.array_to_vector3(position)
            elif isinstance(position, dict):
                pos = {k: v for (k, v) in position.items()}
            else:
                raise Exception(f"Invalid position: {position}")
        if audio_id is None:
            audio_id = Controller.get_unique_id()
        self.commands.append({"$type": "play_audio_from_streaming_assets",
                              "id": audio_id,
                              "path": path,
                              "position": pos,
                              "spatialize": spatialize,
                              "loop": loop})
        if object_id is not None and position is not None:
            self.commands.append({"$type": "parent_audio_source_to_object",
                                  "object_id": object_id,
                                  "audio_id": audio_id})

    def _get_sensor_command_name(self) -> str:
        return "add_audio_sensor"

    def _get_play_audio_command_name(self) -> str:
        return "play_audio_data"
