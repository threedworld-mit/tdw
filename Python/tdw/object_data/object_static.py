import numpy as np


class ObjectStatic:
    """
    Static data for an object. This data won't change between frames.
    """

    def __init__(self, name: str, object_id: int, mass: float, segmentation_color: np.array, size: np.array,
                 category: str, kinematic: bool, dynamic_friction: float, static_friction: float, bounciness: float):
        """
        :param name: The name of the object.
        :param object_id: The unique ID of the object.
        :param mass: The mass of the object.
        :param segmentation_color: The segmentation color of the object.
        :param size: The size of the object.
        :param dynamic_friction: The dynamic friction of the object.
        :param static_friction: The static friction of the object.
        :param bounciness: The bounciness of the object.
        :param kinematic: If True, this object is kinematic, and won't respond to physics.
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
        """:field
        The dynamic friction of the object.
        """
        self.dynamic_friction: float = dynamic_friction
        """:field
        The static friction of the object.
        """
        self.static_friction: float = static_friction
        """:field
        The bounciness of the object.
        """
        self.bounciness: float = bounciness
