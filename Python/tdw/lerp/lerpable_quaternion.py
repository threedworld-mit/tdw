import numpy as np
from tdw.lerp.lerpable import Lerpable
from tdw.tdw_utils import TDWUtils


class LerpableQuaternion(Lerpable[np.ndarray]):
    """
    A numpy array of a 4-element quaternion that can be linearly interpolated between minimum and maximum values.
    """

    def _lerp(self) -> np.ndarray:
        return TDWUtils.slerp(self._a, self._b, self._t)

    def _copy(self, v: np.ndarray) -> np.ndarray:
        return np.copy(v)
