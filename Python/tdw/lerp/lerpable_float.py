from tdw.lerp.lerpable import Lerpable
from tdw.tdw_utils import TDWUtils


class LerpableFloat(Lerpable[float]):
    """
    A float that can be linearly interpolated between minimum and maximum values.
    """

    def _lerp(self) -> float:
        return TDWUtils.lerp(self._a, self._b, self._t)

    def _copy(self, v: float) -> float:
        return v
