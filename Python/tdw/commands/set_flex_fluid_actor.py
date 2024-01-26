# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.set_flex_actor import SetFlexActor


class SetFlexFluidActor(SetFlexActor):
    """
    Create or adjust a FlexArrayActor as a fluid object.
    """

    def __init__(self, id: int, mesh_expansion: float = 0, max_particles: int = 10000, particle_spacing: float = 0.125, mass_scale: float = 1, draw_particles: bool = False):
        """
        :param id: The unique object ID.
        :param mesh_expansion: Mesh local scale of the FlexArrayAsset.
        :param max_particles: Maximum number of particles for the Flex Asset.
        :param particle_spacing: Particle spacing of the Flex Asset.
        :param mass_scale: The mass scale factor.
        :param draw_particles: Debug drawing of particles.
        """

        super().__init__(mass_scale=mass_scale, draw_particles=draw_particles, id=id)
        """:field
        Mesh local scale of the FlexArrayAsset.
        """
        self.mesh_expansion: float = mesh_expansion
        """:field
        Maximum number of particles for the Flex Asset.
        """
        self.max_particles: int = max_particles
        """:field
        Particle spacing of the Flex Asset.
        """
        self.particle_spacing: float = particle_spacing