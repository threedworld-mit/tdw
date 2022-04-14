from tdw.obi_data.cloth.tether_particle_group import TetherParticleGroup


class TetherPosition:
    """
    Data for tethering an Obi cloth object to another object.
    """

    def __init__(self, other_id: int, particle_group: TetherParticleGroup):
        """
        :param other_id: The ID of the other object. If this is the same as `object_id` then the cloth will be suspended in mid-air.
        :param particle_group: The [`TetherParticleGroup`](tether_particle_group.md).
        """

        """:field
        The ID of the other object. If this is the same as `object_id` then the cloth will be suspended in mid-air.
        """
        self.other_id: int = other_id
        """:field
        The [`TetherParticleGroup`](tether_particle_group.md).
        """
        self.particle_group: TetherParticleGroup = particle_group

    def to_dict(self) -> dict:
        return {"other_id": self.other_id,
                "particle_group": self.particle_group.name}
