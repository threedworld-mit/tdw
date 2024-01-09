# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.object_command import ObjectCommand


class IgnoreLeapMotionPhysicsHelpers(ObjectCommand):
    """
    Make the object ignore a Leap Motion rig's physics helpers. This is useful for objects that shouldn't be moved, such as kinematic objects.
    """

    def __init__(self, id: int):
        """
        :param id: The unique object ID.
        """

        super().__init__(id=id)
