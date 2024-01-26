# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.command import Command


class ParentAudioSourceToObject(Command):
    """
    Parent an audio source to an object. When the object moves, the audio source will move with it.
    """

    def __init__(self, audio_id: int, object_id: int):
        """
        :param audio_id: The audio source ID.
        :param object_id: The object ID.
        """

        super().__init__()
        """:field
        The object ID.
        """
        self.object_id: int = object_id
        """:field
        The audio source ID.
        """
        self.audio_id: int = audio_id