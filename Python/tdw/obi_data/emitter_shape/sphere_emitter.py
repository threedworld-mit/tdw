from tdw.obi_data.emitter_shape.emitter_shape import EmitterShape
from tdw.obi_data.emitter_shape.emitter_sampling_method import EmitterSamplingMethod


class SphereEmitter(EmitterShape):
    """
    A sphere-shaped Obi fluid emitter.
    """

    def __init__(self, radius: float = 0.5, sampling_method: EmitterSamplingMethod = EmitterSamplingMethod.volume):
        """
        Create a cube-shaped fluid emitter.

        :param radius: The radius of the sphere.
        :param sampling_method: The [`SamplingMethod`](sampling_method).
        """

        """:field
        The radius of the sphere.
        """
        self.radius: float = radius
        """:field
        The [`SamplingMethod`](sampling_method).
        """
        self.sampling_method: EmitterSamplingMethod = sampling_method

    def _get_type(self) -> str:
        return "sphere_emitter"

    def _get_dict(self) -> dict:
        return {"radius": self.radius,
                "sampling_method": self.sampling_method.name}
