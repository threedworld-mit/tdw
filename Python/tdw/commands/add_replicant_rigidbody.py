# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.replicant_command import ReplicantCommand


class AddReplicantRigidbody(ReplicantCommand):
    """
    Add a Rigidbody to a Replicant.
    """

    def __init__(self, id: int, is_kinematic: bool = True, use_gravity: bool = False):
        """
        :param id: The unique object ID.
        :param is_kinematic: If True, the Rigidbody will be kinematic, and won't respond to physics.
        :param use_gravity: If True, the object will respond to gravity.
        """

        super().__init__(id=id)
        """:field
        If True, the Rigidbody will be kinematic, and won't respond to physics.
        """
        self.is_kinematic: bool = is_kinematic
        """:field
        If True, the object will respond to gravity.
        """
        self.use_gravity: bool = use_gravity