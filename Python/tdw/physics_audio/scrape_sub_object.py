class ScrapeSubObject:
    """
    Data for a sub-object of a model being used as a scrape surface.
    """

    def __init__(self, name: str, material_index: int):
        """
        :param name: The name of the sub-object.
        :param material_index: The index of the material. If you're not sure what this should be, try 0.
        """

        """:field
        The name of the sub-object.
        """
        self.name: str = name
        """:field
        The index of the material. If you're not sure what this should be, try 0.
        """
        self.material_index: int = material_index
