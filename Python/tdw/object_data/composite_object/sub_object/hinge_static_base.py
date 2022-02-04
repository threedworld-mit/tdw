from abc import ABC, abstractmethod
import numpy as np
from tdw.output_data import StaticCompositeObjects
from tdw.object_data.composite_object.sub_object.sub_object_static import SubObjectStatic


class HingeStaticBase(SubObjectStatic, ABC):
    """
    Static data for a light sub-object of a composite object.
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
        If True, the hinge has angular limits.
        """
        self.has_limits: bool = self._get_has_limits(static_composite_objects=static_composite_objects,
                                                     object_index=object_index, sub_object_index=sub_object_index)
        """:field
        The minimum angle from the hinge's resting position in degrees.
        """
        self.min_limit: float = self._get_min_limit(static_composite_objects=static_composite_objects,
                                                    object_index=object_index, sub_object_index=sub_object_index)
        """:field
        The maximum angle from the hinge's resting position in degrees.
        """
        self.max_limit: float = self._get_max_limit(static_composite_objects=static_composite_objects,
                                                    object_index=object_index, sub_object_index=sub_object_index)
        """:field
        The axis of rotation.
        """
        self.axis: np.array = self._get_axis(static_composite_objects=static_composite_objects,
                                             object_index=object_index, sub_object_index=sub_object_index)

    @abstractmethod
    def _get_has_limits(self, static_composite_objects: StaticCompositeObjects, object_index: int,
                        sub_object_index: int) -> bool:
        """
        :param static_composite_objects: `StaticCompositeObjects` output data.
        :param object_index: The object index.
        :param sub_object_index: The index of this sub-object.

        :return: True if this hinge has angular limits.
        """

        raise Exception()

    @abstractmethod
    def _get_min_limit(self, static_composite_objects: StaticCompositeObjects, object_index: int,
                       sub_object_index: int) -> float:
        """
        :param static_composite_objects: `StaticCompositeObjects` output data.
        :param object_index: The object index.
        :param sub_object_index: The index of this sub-object.

        :return: The minimum angular limit in degrees.
        """

        raise Exception()

    @abstractmethod
    def _get_max_limit(self, static_composite_objects: StaticCompositeObjects, object_index: int,
                       sub_object_index: int) -> float:
        """
        :param static_composite_objects: `StaticCompositeObjects` output data.
        :param object_index: The object index.
        :param sub_object_index: The index of this sub-object.

        :return: The maximum angular limit in degrees.
        """

        raise Exception()

    @abstractmethod
    def _get_axis(self, static_composite_objects: StaticCompositeObjects, object_index: int,
                  sub_object_index: int) -> np.array:
        """
        :param static_composite_objects: `StaticCompositeObjects` output data.
        :param object_index: The object index.
        :param sub_object_index: The index of this sub-object.

        :return: The axis of rotation.
        """

        raise Exception()
