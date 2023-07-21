import numpy as np
from tdw.lerp.lerpable import Lerpable
from tdw.tdw_utils import TDWUtils


class LerpableVector(Lerpable[np.ndarray]):
    """
    A numpy array of a 3-element vector that can be linearly interpolated between minimum and maximum values.
    """

    def get_dt(self) -> float:
        return abs(self._true_dt)

    def _lerp(self) -> np.ndarray:
        return TDWUtils.lerp_array(self._a, self._b, self._t)

    def _copy(self, v: np.ndarray) -> np.ndarray:
        return np.copy(v)

    def _set_increase(self) -> None:
        self._increase = True
        self._t = 0
