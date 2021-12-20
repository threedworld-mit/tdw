from typing import List


class ArrangementResult:
    """
    A description of the result of having called `ProcGenObjectManager.get_arrangement()`.
    """

    def __init__(self, success: bool, object_ids: List[int], kinematic_object_ids: List[int], categories: List[str],
                 commands: List[dict]):
        """
        :param success: If True, the arrangement exists. If False, it wasn't possible to generate the arrangement.
        :param object_ids: The object IDs of every object in the arrangement, including kinematic objects.
        :param kinematic_object_ids: The object IDs of every kinematic object in the arrangement.
        :param categories: A list of the objects' categories. See: `ProcGenObjectManager.MODEL_CATEGORIES`.
        :param commands: A list of commands to send to the build.
        """

        """:field
        If True, the arrangement exists. If False, it wasn't possible to generate the arrangement.
        """
        self.success: bool = success
        """:field
         The object IDs of every object in the arrangement, including kinematic objects.
        """
        self.object_ids: List[int] = object_ids
        """:field
        The object IDs of every kinematic object in the arrangement.
        """
        self.kinematic_object_ids: List[int] = kinematic_object_ids
        """:field
        A list of the objects' categories. See: `ProcGenObjectManager.MODEL_CATEGORIES`.
        """
        self.categories: List[str] = categories
        """:field
        A list of commands to send to the build. If `success == False`, this list is empty.
        """
        self.commands: List[dict] = commands
