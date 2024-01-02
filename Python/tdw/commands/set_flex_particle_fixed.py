# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.flex_object_command import FlexObjectCommand


class SetFlexParticleFixed(FlexObjectCommand):
    """
    Fix the particle in the Flex object, such that it does not move.
    """

    def __init__(self, id: int, particle_id: int, is_fixed: bool):
        """
        :param id: The unique object ID.
        :param particle_id: The ID of the particle.
        :param is_fixed: Set whether particle is fixed or not.
        """

        super().__init__(id=id)
        """:field
        Set whether particle is fixed or not.
        """
        self.is_fixed: bool = is_fixed
        """:field
        The ID of the particle.
        """
        self.particle_id: int = particle_id
