import numpy as np


class ObjectStatic:
    """
    Static data for an object. This data won't change between frames.
    """

    def __init__(self, name: str, object_id: int, mass: float, segmentation_color: np.array, size: np.array,
                 category: str, kinematic: bool):
        """
        :param name: The name of the object.
        :param object_id: The unique ID of the object.
        :param mass: The mass of the object.
        :param segmentation_color: The segmentation color of the object.
        :param size: The size of the object.
        """

        """:field
        The unique ID of the object.
        """
        self.object_id: int = object_id
        """:field
        [The name of the model.](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/librarian/model_librarian.md)
        """
        self.name: str = name.lower()
        """:field
         The semantic category of the object.
         """
        self.category: str = category
        """:field
        If True, this object is kinematic, and won't respond to physics. 
        Examples: a painting hung on a wall or built-in furniture like a countertop.
        """
        self.kinematic = kinematic
        """:field
        The RGB segmentation color for the object as a numpy array: `[r, g, b]`
        """
        self.segmentation_color = segmentation_color
        """:field
        The mass of the object.
        """
        self.mass = mass
        """:field
        The size of the object as a numpy array: `[width, height, length]`
        """
        self.size = size
