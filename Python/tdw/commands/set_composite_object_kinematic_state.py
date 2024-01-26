# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.object_type_command import ObjectTypeCommand


class SetCompositeObjectKinematicState(ObjectTypeCommand):
    """
    Set the top-level Rigidbody of a composite object to be kinematic or not. Optionally, set the same state for all of its sub-objects. A kinematic object won't respond to PhysX physics.
    """

    def __init__(self, id: int, is_kinematic: bool = False, use_gravity: bool = False, sub_objects: bool = False):
        """
        :param id: The unique object ID.
        :param is_kinematic: If True, the top-level Rigidbody will be kinematic, and won't respond to physics.
        :param use_gravity: If True, the top-level object will respond to gravity.
        :param sub_objects: If True, apply the values for is_kinematic and use_gravity to each of the composite object's sub-objects.
        """

        super().__init__(id=id)
        """:field
        If True, the top-level Rigidbody will be kinematic, and won't respond to physics.
        """
        self.is_kinematic: bool = is_kinematic
        """:field
        If True, the top-level object will respond to gravity.
        """
        self.use_gravity: bool = use_gravity
        """:field
        If True, apply the values for is_kinematic and use_gravity to each of the composite object's sub-objects.
        """
        self.sub_objects: bool = sub_objects