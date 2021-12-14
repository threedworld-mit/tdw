from abc import ABC, abstractmethod
from base64 import b64encode
from typing import List, Union, Dict
from pathlib import Path
import wave
import numpy as np
from overrides import final
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.add_on import AddOn
from tdw.audio_constants import SAMPLE_RATE, CHANNELS


class AudioInitializerBase(AddOn, ABC):
    """
    Abstract base class for an audio initializer add-on.
    """

    def __init__(self, avatar_id: str = "a", framerate: int = 60):
        """
        :param avatar_id: The ID of the listening avatar.
        :param framerate: The target simulation framerate.
        """

        super().__init__()
        """:field
        The ID of the listening avatar.
        """
        self.avatar_id: str = avatar_id
        # The target framerate.
        self._target_framerate: int = framerate

    def get_initialization_commands(self) -> List[dict]:
        """
        This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

        :return: A list of commands that will initialize this add-on.
        """

        return [{"$type": "set_target_framerate",
                 "framerate": self._target_framerate},
                {"$type": self._get_sensor_command_name(),
                 "avatar_id": self.avatar_id}]

    @final
    def on_send(self, resp: List[bytes]) -> None:
        """
        This is called after commands are sent to the build and a response is received.

        Use this function to send commands to the build on the next frame, given the `resp` response.
        Any commands in the `self.commands` list will be sent on the next frame.

        :param resp: The response from the build.
        """

        return

    @final
    def play(self, path: Union[str, Path], position: Union[np.array, Dict[str, float]], audio_id: int = None,
             object_id: int = None) -> None:
        """
        Load a .wav file and prepare to send a command to the build to play the audio.
        The command will be sent on the next `Controller.communicate()` call.

        :param path: The path to a .wav file.
        :param position: The position of audio source. Can be a numpy array or x, y, z dictionary.
        :param audio_id: The unique ID of the audio source. If None, a random ID is generated.
        :param object_id: If not None, parent the audio source to this object.
        """

        if isinstance(path, Path):
            path = str(path.resolve())
        if isinstance(position, np.ndarray):
            position = TDWUtils.array_to_vector3(position)
        if audio_id is None:
            audio_id = Controller.get_unique_id()
        w = wave.open(path, 'rb')
        wav = w.readframes(w.getparams().nframes)
        self.commands.append({"$type": self._get_play_audio_command_name(),
                              "id": audio_id,
                              "position": position,
                              "num_frames": len(wav),
                              "num_channels": CHANNELS,
                              "frame_rate": SAMPLE_RATE,
                              "wav_data": str(b64encode(wav), 'ascii', 'ignore')})
        if object_id is not None:
            self.commands.append({"$type": "parent_audio_source_to_object",
                                  "object_id": object_id,
                                  "audio_id": audio_id})

    @abstractmethod
    def _get_sensor_command_name(self) -> str:
        """
        :return: The name of the command to add an audio sensor.
        """

        raise Exception()

    @abstractmethod
    def _get_play_audio_command_name(self) -> str:
        """
        :return: The name of the command to play audio.
        """

        raise Exception()
