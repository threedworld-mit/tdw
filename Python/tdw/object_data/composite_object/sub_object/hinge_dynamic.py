from tdw.object_data.composite_object.sub_object.sub_object_dynamic import SubObjectDynamic


class HingeDynamic(SubObjectDynamic):
    """
    Dynamic data for a hinge, motor, or spring sub-object of a composite object.
    """

    def __init__(self, angle: float, velocity: float, sub_object_id: int):
        """
        :param angle: The angle in degrees of the hinge relative to its resting position.
        :param velocity: The angular velocity in degrees per second of the hinge.
        :param sub_object_id: The ID of this sub-object.
        """

        super().__init__(sub_object_id=sub_object_id)
        """:field
        The angle in degrees of the hinge relative to its resting position.
        """
        self.angle: float = angle
        """:field
        The angular velocity in degrees per second of the hinge.
        """
        self.velocity: float = velocity
