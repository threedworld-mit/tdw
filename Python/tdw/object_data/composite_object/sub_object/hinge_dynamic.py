from tdw.output_data import DynamicCompositeObjects
from tdw.object_data.composite_object.sub_object.sub_object_dynamic import SubObjectDynamic


class HingeDynamic(SubObjectDynamic):
    """
    Dynamic data for a hinge, motor, or spring sub-object of a composite object.
    """

    def __init__(self, dynamic_composite_objects: DynamicCompositeObjects, object_index: int, sub_object_index: int):
        """
        :param dynamic_composite_objects: `DynamicCompositeObjects` output data.
        :param object_index: The object index.
        :param sub_object_index: The index of this sub-object.
        """

        super().__init__(dynamic_composite_objects=dynamic_composite_objects, object_index=object_index,
                         sub_object_index=sub_object_index)
        """:field
        The angle in degrees of the hinge relative to its resting position.
        """
        self.angle: float = dynamic_composite_objects.get_hinge_angle(object_index, sub_object_index)
        """:field
        The angular velocity in degrees per second of the hinge.
        """
        self.velocity: float = dynamic_composite_objects.get_hinge_velocity(object_index, sub_object_index)

    def _get_sub_object_id(self, dynamic_composite_objects: DynamicCompositeObjects, object_index: int,
                           sub_object_index: int) -> int:
        return dynamic_composite_objects.get_hinge_id(object_index, sub_object_index)
