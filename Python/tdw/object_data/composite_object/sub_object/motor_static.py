import numpy as np
from tdw.output_data import StaticCompositeObjects
from tdw.object_data.composite_object.sub_object.hinge_static_base import HingeStaticBase


class MotorStatic(HingeStaticBase):
    """
    Static data for a motor sub-object of a composite object.
    """

    def __init__(self, static_composite_objects: StaticCompositeObjects, object_index: int, sub_object_index: int):
        """
        :param static_composite_objects: `StaticCompositeObjects` output data.
        :param object_index: The object index.
        :param sub_object_index: The index of this sub-object.
        """

        super().__init__(static_composite_objects=static_composite_objects, object_index=object_index,
                         sub_object_index=sub_object_index)
        """:field
        The force limit.
        """
        self.force: float = static_composite_objects.get_motor_force(object_index, sub_object_index)

    def _get_sub_object_id(self, static_composite_objects: StaticCompositeObjects, object_index: int,
                           sub_object_index: int) -> int:
        return static_composite_objects.get_motor_id(object_index, sub_object_index)

    def _get_has_limits(self, static_composite_objects: StaticCompositeObjects, object_index: int,
                        sub_object_index: int) -> bool:
        return static_composite_objects.get_motor_has_limits(object_index, sub_object_index)

    def _get_min_limit(self, static_composite_objects: StaticCompositeObjects, object_index: int,
                       sub_object_index: int) -> float:
        return static_composite_objects.get_motor_min_limit(object_index, sub_object_index)

    def _get_max_limit(self, static_composite_objects: StaticCompositeObjects, object_index: int,
                       sub_object_index: int) -> float:
        return static_composite_objects.get_motor_max_limit(object_index, sub_object_index)

    def _get_axis(self, static_composite_objects: StaticCompositeObjects, object_index: int,
                  sub_object_index: int) -> np.ndarray:
        return np.array(static_composite_objects.get_motor_axis(object_index, sub_object_index))
