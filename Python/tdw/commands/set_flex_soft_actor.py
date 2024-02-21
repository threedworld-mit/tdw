# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.set_flex_actor import SetFlexActor


class SetFlexSoftActor(SetFlexActor):
    """
    Create or adjust a FlexSoftActor for the object.
    """

    def __init__(self, id: int, volume_sampling: float = 2.0, surface_sampling: float = 0, cluster_spacing: float = 0.2, cluster_radius: float = 0.2, cluster_stiffness: float = 0.2, link_radius: float = 0.1, link_stiffness: float = 0.5, particle_spacing: float = 0.02, skinning_falloff: float = 1.0, mass_scale: float = 1, draw_particles: bool = False):
        """
        :param id: The unique object ID.
        :param volume_sampling: The volumne sampling factor.
        :param surface_sampling: The surface sampling factor.
        :param cluster_spacing: The cluster spacing.
        :param cluster_radius: The cluster radius.
        :param cluster_stiffness: The cluster stiffness.
        :param link_radius: The link radius.
        :param link_stiffness: The link stiffness.
        :param particle_spacing: Particle spacing of the Flex Asset.
        :param skinning_falloff: Skinning falloff of the FlexSoftSkinning component.
        :param mass_scale: The mass scale factor.
        :param draw_particles: Debug drawing of particles.
        """

        super().__init__(mass_scale=mass_scale, draw_particles=draw_particles, id=id)
        """:field
        The volumne sampling factor.
        """
        self.volume_sampling: float = volume_sampling
        """:field
        The surface sampling factor.
        """
        self.surface_sampling: float = surface_sampling
        """:field
        The cluster spacing.
        """
        self.cluster_spacing: float = cluster_spacing
        """:field
        The cluster radius.
        """
        self.cluster_radius: float = cluster_radius
        """:field
        The cluster stiffness.
        """
        self.cluster_stiffness: float = cluster_stiffness
        """:field
        The link radius.
        """
        self.link_radius: float = link_radius
        """:field
        The link stiffness.
        """
        self.link_stiffness: float = link_stiffness
        """:field
        Particle spacing of the Flex Asset.
        """
        self.particle_spacing: float = particle_spacing
        """:field
        Skinning falloff of the FlexSoftSkinning component.
        """
        self.skinning_falloff: float = skinning_falloff