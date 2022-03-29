from typing import Dict
from tdw.obi_data.fluids.emitter_shape import EmitterShape
from tdw.obi_data.fluids.emitter_sampling_method import EmitterSamplingMethod


class CubeEmitter(EmitterShape):
    """
    A cube-shaped Obi fluid emitter.
    """

    def __init__(self, size: Dict[str, float] = None,
                 sampling_method: EmitterSamplingMethod = EmitterSamplingMethod.volume):
        """
        :param size: The size of the cube in meters. If None, defaults to `{"x": 0.1, "y": 0.1, "z": 0.1}`.
        :param sampling_method: The [`EmitterSamplingMethod`](emitter_sampling_method.md).
        """

        if size is None:
            """:field
            The size of the cube in meters. If None, defaults to `{"x": 0.1, "y": 0.1, "z": 0.1}`.
            """
            self.size: Dict[str, float] = {"x": 0.1, "y": 0.1, "z": 0.1}
        else:
            self.size = size
        """:field
        The [`EmitterSamplingMethod`](emitter_sampling_method.md).
        """
        self.sampling_method: EmitterSamplingMethod = sampling_method

    def _get_type(self) -> str:
        return "cube_emitter"

    def _get_dict(self) -> dict:
        return {"size": self.size,
                "sampling_method": self.sampling_method.name}
