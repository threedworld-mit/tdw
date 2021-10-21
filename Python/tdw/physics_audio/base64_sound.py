import base64
from pathlib import Path
from typing import Union
import wave
import numpy as np
from tdw.audio_constants import SAMPLE_RATE, CHANNELS, SAMPLE_WIDTH


class Base64Sound:
    """
    A sound encoded as a base64 string.
    """

    def __init__(self, snd: np.array):
        """
        :param snd: The sound byte array.
        """

        """:field
        Byte data of the sound.
        """
        self.bytes: bytes = bytes(np.array(snd * 32767, dtype='int16'))
        """:field
        A base64 string of the sound. Send this to the build.
        """
        self.wav_str = base64.b64encode(self.bytes).decode('utf-8')
        """:field
        The length of the byte array.
        """
        self.length: int = len(self.bytes)

    def write(self, path: Union[str, Path]) -> None:
        """
        Write audio to disk.

        :param path: The path to the .wav file.
        """

        if isinstance(path, Path):
            path = str(path.resolve())
        w = wave.Wave_write(f=path)
        w.setnchannels(CHANNELS)
        w.setnframes(self.length)
        w.setframerate(SAMPLE_RATE)
        w.setsampwidth(SAMPLE_WIDTH)
        w.writeframes(self.bytes)
