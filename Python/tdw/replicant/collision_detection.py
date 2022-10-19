from typing import List


class CollisionDetection:
    """
    Parameters for how a Replicant handles collision detection.
    """

    def __init__(self, objects: bool = True, avoid: bool = True, held: bool = True, exclude_objects: List[int] = None,
                 previous_was_same: bool = True):
        """
        :param objects: If True, the Replicant will stop when it collides with an object unless the is in the `exclude_objects`.
        :param avoid: If True, while walking, the Replicant will try to stop *before* colliding with objects.
        :param held: If True, ignore collisions between a held object and hand + lower arm holding the object.
        :param exclude_objects: The Replicant will ignore a collision with any object in this list, *regardless* of whether or not `objects == True`. Can be None.
        :param previous_was_same: If True, the Replicant will stop if the previous action resulted in a collision and was the same sort of action as the current one.
        """

        """:field
        If True, the Replicant will stop when it collides with an object unless the is in the `exclude_objects`.
        """
        self.objects: bool = objects
        """:field
        If True, while walking, the Replicant will try to stop *before* colliding with objects.
        """
        self.avoid: bool = avoid
        """:field
        If True, ignore collisions between a held object and hand + lower arm holding the object.
        """
        self.held: bool = held
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
