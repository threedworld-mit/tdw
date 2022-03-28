from tdw.obi_data.fluids.emitter_shape import EmitterShape


class DiskEmitter(EmitterShape):
    """
    A disk-shaped Obi fluid emitter.
    """

    def __init__(self, radius: float = 0.1, edge_emission: bool = False):
        """
        :param radius: The radius of the circle.
        :param edge_emission: If enabled, particles will be emitted from the circle's edges, instead of its interior.
        """

        """:field
        The radius of the circle.
        """
        self.radius: float = radius
        """:field
        If enabled, particles will be emitted from the circle's edges, instead of its interior.
        """
        self.edge_emission: bool = edge_emission

    def _get_type(self) -> str:
        return "disk_emitter"

    def _get_dict(self) -> dict:
        return {"radius": self.radius,
                "edge_emission": self.edge_emission}
