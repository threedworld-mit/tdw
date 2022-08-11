from tdw.object_data.composite_object.sub_object.sub_object_dynamic import SubObjectDynamic


class LightDynamic(SubObjectDynamic):
    """
    Dynamic data for a light sub-object of a composite object.
    """

    def __init__(self, is_on: bool, sub_object_id: int):
        """
        :param is_on: If True, the light is on.
        :param sub_object_id: The ID of this sub-object.
        """

        super().__init__(sub_object_id=sub_object_id)
        """:field
        If True, the light is on.
        """
        self.is_on: bool = bool(is_on)
