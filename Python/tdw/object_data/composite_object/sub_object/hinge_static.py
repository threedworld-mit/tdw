import numpy as np
from tdw.output_data import StaticCompositeObjects
from tdw.object_data.composite_object.sub_object.hinge_static_base import HingeStaticBase


class HingeStatic(HingeStaticBase):
    """
    Static data for a hinge sub-object of a composite object.
    """

    def _get_sub_object_id(self, static_composite_objects: StaticCompositeObjects, object_index: int,
                           sub_object_index: int) -> int:
        return static_composite_objects.get_hinge_id(object_index, sub_object_index)

    def _get_has_limits(self, static_composite_objects: StaticCompositeObjects, object_index: int,
                        sub_object_index: int) -> bool:
        return static_composite_objects.get_hinge_has_limits(object_index, sub_object_index)

    def _get_min_limit(self, static_composite_objects: StaticCompositeObjects, object_index: int,
                       sub_object_index: int) -> float:
        return static_composite_objects.get_hinge_min_limit(object_index, sub_object_index)

    def _get_max_limit(self, static_composite_objects: StaticCompositeObjects, object_index: int,
                       sub_object_index: int) -> float:
        return static_composite_objects.get_hinge_max_limit(object_index, sub_object_index)

    def _get_axis(self, static_composite_objects: StaticCompositeObjects, object_index: int,
                  sub_object_index: int) -> np.array:
        return np.array(static_composite_objects.get_hinge_axis(object_index, sub_object_index))
