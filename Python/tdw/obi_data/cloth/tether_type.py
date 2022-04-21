class TetherType:
    """
    A type of an Obi cloth tether position.
    """

    def __init__(self, object_id: int, is_static: bool = True):
        """
        :param object_id: The object ID. If this is the same as the cloth's ID, the cloth will be suspended in mid-air.
        :param is_static: If True, this is a static tether attachment. If False, this is a dynamic tether attachment.
        """

        """:field
        The object ID. If this is the same as the cloth's ID, the cloth will be suspended in mid-air.
        """
        self.object_id: int = object_id
        """:field
        If True, this is a static tether attachment. If False, this is a dynamic tether attachment.
        """
        self.is_static: bool = is_static
