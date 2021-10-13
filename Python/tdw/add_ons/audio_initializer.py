from tdw.add_ons.audio_initializer_base import AudioInitializerBase


class AudioInitializer(AudioInitializerBase):
    """
    Initialize standard (Unity) audio.

    This assumes that an avatar corresponding to `avatar_id` has already been added to the scene.
    """

    def __init__(self, avatar_id: str = "a", framerate: int = 60):
        """
        :param avatar_id: The ID of the listening avatar.
        :param framerate: The target simulation framerate.
        """

        super().__init__(avatar_id=avatar_id, framerate=framerate)

    def _get_sensor_command_name(self) -> str:
        return "add_audio_sensor"

    def _get_play_audio_command_name(self) -> str:
        return "play_audio_data"
