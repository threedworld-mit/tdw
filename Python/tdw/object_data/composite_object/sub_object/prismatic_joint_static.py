import numpy as np
from tdw.output_data import StaticCompositeObjects
from tdw.object_data.composite_object.sub_object.sub_object_static import SubObjectStatic


class PrismaticJointStatic(SubObjectStatic):
    """
    Static data for a prismatic joint sub-object of a composite object.
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
        The linear limit.
        """
        self.limit: float = static_composite_objects.get_prismatic_joint_limit(object_index, sub_object_index)
        """:field
        The axis of movement.
        """
        self.axis: np.ndarray = np.array(static_composite_objects.get_prismatic_joint_axis(object_index, sub_object_index))

    def _get_sub_object_id(self, static_composite_objects: StaticCompositeObjects, object_index: int,
                           sub_object_index: int) -> int:
        return static_composite_objects.get_prismatic_joint_id(object_index, sub_object_index)
