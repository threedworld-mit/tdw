from abc import ABC


class SubObjectDynamic(ABC):
    """
    Abstract class for static data for a sub-object of a composite object.
    """

    def __init__(self, sub_object_id: int):
        """
        :param sub_object_id: The ID of this sub-object.
        """

        """:field
        The ID of this sub-object.
        """
        self.sub_object_id: int = int(sub_object_id)
