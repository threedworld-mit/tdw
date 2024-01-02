# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.add_audio_sensor_command import AddAudioSensorCommand


class AddAudioSensor(AddAudioSensorCommand):
    """
    Add an AudioSensor component to the avatar, if it does not already have one.
    """

    def __init__(self, avatar_id: str = "a"):
        """
        :param avatar_id: The ID of the avatar.
        """

        super().__init__(avatar_id=avatar_id)

