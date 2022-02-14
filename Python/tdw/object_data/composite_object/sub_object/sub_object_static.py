from abc import ABC, abstractmethod
from tdw.output_data import StaticCompositeObjects


class SubObjectStatic(ABC):
    """
    Abstract class for static data for a sub-object of a composite object.
    """

    def __init__(self, static_composite_objects: StaticCompositeObjects, object_index: int, sub_object_index: int):
        """
        :param static_composite_objects: `StaticCompositeObjects` output data.
        :param object_index: The object index.
        :param sub_object_index: The index of this sub-object.
        """

        """:field
        The ID of this sub-object.
        """
        self.sub_object_id: int = self._get_sub_object_id(static_composite_objects=static_composite_objects,
                                                          object_index=object_index,
                                                          sub_object_index=sub_object_index)

    @abstractmethod
    def _get_sub_object_id(self, static_composite_objects: StaticCompositeObjects, object_index: int,
                           sub_object_index: int) -> int:
        """
        :param static_composite_objects: `StaticCompositeObjects` output data.
        :param object_index: The object index.
        :param sub_object_index: The index of this sub-object.

        :return: The sub-object ID.
        """

        raise Exception()
