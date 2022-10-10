from typing import List


class CollisionDetection:
    """
    Parameters for how a Replicant handles collision detection.
    """

    def __init__(self, walls: bool = False, floor: bool = False, objects: bool = False, avoid: bool = True,
                 include_objects: List[int] = None, exclude_objects: List[int] = None,
                 previous_was_same: bool = True):
        """
        :param walls: If True, the Replicant will stop when it collides with a wall.
        :param floor: If True, the Replicant will stop when it collides with the floor.
        :param objects: If True, the Replicant will stop when it collides collides with an object with a mass greater than the `mass` value unless the object is in the `exclude_objects`.
        :param avoid: If True, while walking, the Replicant will try to stop *before* colliding with objects.
        :param include_objects: The Replicant will stop if it collides with any object in this list, whether or not `objects == True`, or the mass of the object. Can be None.
        :param exclude_objects: The Replicant will ignore a collision with any object in this list, *regardless* of whether or not `objects == True`. Can be None.
        :param previous_was_same: If True, the Replicant will stop if the previous action resulted in a collision and was the same sort of action as the current one.
        """

        """:field
        If True, the Replicant will stop when it collides with a wall.
        """
        self.walls: bool = walls
        """:field
        If True, the Replicant will stop when it collides with the floor.
        """
        self.floor: bool = floor
        """:field
        If True, the Replicant will stop when it collides with an object with a mass greater than the `mass` value unless the object is in the `exclude_objects`.
        """
        self.objects: bool = objects
        """:field
        If True, while walking, the Replicant will try to stop *before* colliding with objects.
        """
        self.avoid: bool = avoid
        if include_objects is None:
            """:field
            The Replicant will stop if it collides with any object in this list, *regardless* of mass, whether or not `objects == True`, or the mass of the object. Can be None.
            """
            self.include_objects: List[int] = list()
        else:
            self.include_objects: List[int] = include_objects
        if exclude_objects is None:
            """:field
            The Replicant will ignore a collision with any object in this list, *regardless* of whether or not `objects == True` or the mass of the object. Can be None.
            """
            self.exclude_objects: List[int] = list()
        else:
            self.exclude_objects: List[int] = exclude_objects
        """:field
        If True, the Replicant will stop if the previous action resulted in a collision and was the same sort of action as the current one.
        """
        self.previous_was_same: bool = previous_was_same
