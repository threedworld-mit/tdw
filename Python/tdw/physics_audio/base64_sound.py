import base64
import numpy as np


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
