from tdw.obi_data.fluids.emitter_shape import EmitterShape


class EdgeEmitter(EmitterShape):
    """
    A linear-shaped Obi fluid emitter.
    """

    def __init__(self, length: float = 0.1, radial_velocity: float = 1):
        """
        :param length: The length of the edge.
        :param radial_velocity: The velocity twisting along the length of the edge.
        """

        """:field
        The length of the edge.
        """
        self.length: float = length
        """:field
        The velocity twisting along the length of the edge.
        """
        self.radial_velocity: float = radial_velocity

    def _get_type(self) -> str:
        return "edge_emitter"

    def _get_dict(self) -> dict:
        return {"length": self.length,
                "radial_velocity": self.radial_velocity}
