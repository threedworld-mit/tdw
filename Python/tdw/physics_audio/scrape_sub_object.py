class ScrapeSubObject:
    """
    Data for a sub-object of a model being used as a scrape surface.
    """

    def __init__(self, sub_object_name: str, material_index: int):
        """
        :param sub_object_name: The name of the sub-object.
        :param material_index: The index of the material.
        """

        """:field
        The name of the sub-object.
        """
        self.sub_object_name: str = sub_object_name
        """:field
        The index of the material.
        """
        self.material_index: int = material_index
