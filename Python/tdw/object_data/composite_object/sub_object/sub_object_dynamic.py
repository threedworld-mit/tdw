from abc import ABC, abstractmethod
from tdw.output_data import DynamicCompositeObjects


class SubObjectDynamic(ABC):
    """
    Abstract class for static data for a sub-object of a composite object.
    """

    def __init__(self, dynamic_composite_objects: DynamicCompositeObjects, object_index: int, sub_object_index: int):
        """
        :param dynamic_composite_objects: `DynamicCompositeObjects` output data.
        :param object_index: The object index.
        :param sub_object_index: The index of this sub-object.
        """

        """:field
        The ID of this sub-object.
        """
        self.sub_object_id: int = self._get_sub_object_id(dynamic_composite_objects=dynamic_composite_objects,
                                                          object_index=object_index,
                                                          sub_object_index=sub_object_index)

    @abstractmethod
    def _get_sub_object_id(self, dynamic_composite_objects: DynamicCompositeObjects, object_index: int,
                           sub_object_index: int) -> int:
        """
        :param dynamic_composite_objects: `DynamicCompositeObjects` output data.
        :param object_index: The object index.
        :param sub_object_index: The index of this sub-object.

        :return: The sub-object ID.
        """

        raise Exception()
