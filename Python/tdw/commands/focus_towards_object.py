# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.focus_on_object_command import FocusOnObjectCommand


class FocusTowardsObject(FocusOnObjectCommand):
    """
    Focus towards the depth-of-field towards the position of an object.
    """

    def __init__(self, object_id: int, speed: float = 0.3, use_centroid: bool = False, sensor_name: str = "SensorContainer", avatar_id: str = "a"):
        """
        :param object_id: The ID of the object.
        :param speed: Focus towards the target distance at this speed.
        :param use_centroid: If true, look at the centroid of the object. This is computationally expensive. If false, look at the position of the object (y=0).
        :param sensor_name: The name of the target sensor.
        :param avatar_id: The ID of the avatar.
        """

        super().__init__(object_id=object_id, use_centroid=use_centroid, sensor_name=sensor_name, avatar_id=avatar_id)
        """:field
        Focus towards the target distance at this speed.
        """
        self.speed: float = speed
