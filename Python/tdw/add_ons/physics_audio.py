from os import devnull
from subprocess import call
from typing import List, Union
from pathlib import Path
import numpy as np
from tdw.output_data import OutputData, AudioSources, Rigidbodies, Transforms
from tdw.tdw_utils import AudioUtils
from tdw.add_ons.add_on import AddOn


class PhysicsAudio(AddOn):
    """
    Record audio from a TDW build.
    """

    def __init__(self, avatar_id: str, max_frames: int = -1, resonance_audio: bool = False):
        """
        :param max_frames: If greater than 0, stop recording after this many frames even if objects are still moving or making sound.
        """

        super().__init__()

        """:field
        The ID of the avatar.
        """
        self.avatar_id: str = avatar_id
        """:field
        If True, this simulation is using Resonance Audio.
        """
        self.resonance_audio: bool = resonance_audio
        """:field
        If greater than 0, stop recording after this many frames even if objects are still moving or making sound.
        """
        self.max_frames: int = max_frames
        # The current frame.
        self._frame: int = 0
        """:field
        If recording audio, this is the output path.
        """
        self.output_path: Path = Path.home()

    def get_initialization_commands(self) -> List[dict]:
        return [{"$type": "add_environ_audio_sensor" if self.resonance_audio else "add_audio_sensor",
                 "avatar_id": self.avatar_id},
                {"$type": "send_rigidbodies",
                 "frequency": "always"},
                {"$type": "send_collisions",
                 "enter": True,
                 "stay": True,
                 "exit": True,
                 "collision_types": ["obj", "env"]}]

    def on_send(self, resp: List[bytes]) -> None:
        if PhysicsAudio.is_recording():
            # Stop recording at the maximum number of frames.
            self._frame += 1
            if 0 < self.max_frames <= self._frame:
                self.stop_recording()
            else:
                # Get any objects that fell below the floor.
                below_floor: List[int] = list()
                for i in range(len(resp) - 1):
                    r_id = OutputData.get_data_type_id(resp[i])
                    if r_id == "tran":
                        transforms = Transforms(resp[i])
                        for j in range(transforms.get_num()):
                            if transforms.get_position(j)[1] < -0.1:
                                below_floor.append(transforms.get_id(j))
                # Check if objects have stopped moving and no audio is playing.
                sleeping = True
                playing_audio = False
                for i in range(len(resp) - 1):
                    r_id = OutputData.get_data_type_id(resp[i])
                    if r_id == "rigi":
                        rigidbodies = Rigidbodies(resp[i])
                        for j in range(rigidbodies.get_num()):
                            if rigidbodies.get_id(j) not in below_floor and not rigidbodies.get_sleeping(j):
                                sleeping = False
                                break
                    elif r_id == "audi":
                        audio_sources = AudioSources(resp[i])
                        for j in range(audio_sources.get_num()):
                            if audio_sources.get_is_playing(j):
                                playing_audio = True
                                break
                        # Check if the simulation is totally silent (there might be Resonance Audio reverb).
                        if not playing_audio and np.max(audio_sources.get_samples()) > 0:
                            playing_audio = True
                if sleeping and not playing_audio:
                    self.stop_recording()

    def start_recording(self, output_path: Union[str, Path]) -> None:
        """
        Start recording.

        :param output_path: The path to the output .wav file.
        """

        # Don't start a new recording if one is ongoing.
        if PhysicsAudio.is_recording():
            return

        if isinstance(output_path, str):
            self.output_path = Path(output_path)
        if not output_path.parent.exists:
            self.output_path.parent.mkdir(parents=True)

        self._frame = 0
        # Start listening.
        AudioUtils.start(output_path=self.output_path)
        self.commands.extend([{"$type": "send_audio_sources",
                               "frequency": "always"},
                              {"$type": "send_transforms",
                               "frequency": "always"}])

    @staticmethod
    def is_recording() -> bool:
        """
        :return: True if there is a recording in-progress.
        """

        return AudioUtils.is_recording()

    def stop_recording(self) -> None:
        """
        Stop an ongoing recording. Use ffmpeg to remove initial silence.
        """

        AudioUtils.stop()
        # Use ffmpeg to remove the initial silence.
        with open(devnull, "w+") as f:
            call(["ffmpeg", "-i", str(self.output_path.resolve()),
                  "-ss", "00:00:00.1",
                  str(self.output_path.resolve())],
                 stderr=f)
        self.commands.append({"$type": "send_audio_sources",
                              "frequency": "never"})
