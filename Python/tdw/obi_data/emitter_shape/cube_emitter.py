from typing import Dict
from tdw.obi_data.emitter_shape.emitter_shape import EmitterShape
from tdw.obi_data.emitter_shape.emitter_sampling_method import EmitterSamplingMethod


class CubeEmitter(EmitterShape):
    """
    A cube-shaped Obi fluid emitter.
    """

    def __init__(self, size: Dict[str, float] = None, sampling_method: EmitterSamplingMethod = EmitterSamplingMethod.volume):
        """
        Create a cube-shaped fluid emitter.

        :param size: The size of the cube in meters. If None, defaults to (1, 1, 1).
        :param sampling_method: The [`SamplingMethod`](sampling_method).
        """

        if size is None:
            """:field
            The size of the cube in meters. If None, defaults to (1, 1, 1).
            """
            self.size: Dict[str, float] = {"x": 1, "y": 1, "z": 1}
        else:
            self.size = size
        """:field
        The [`SamplingMethod`](sampling_method).
        """
        self.sampling_method: EmitterSamplingMethod = sampling_method

    def _get_type(self) -> str:
        return "cube_emitter"

    def _get_dict(self) -> dict:
        return {"size": self.size,
                "sampling_method": self.sampling_method.name}
