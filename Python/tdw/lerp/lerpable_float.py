from tdw.lerp.lerpable import Lerpable
from tdw.tdw_utils import TDWUtils


class LerpableFloat(Lerpable[float]):
    """
    A float that can be linearly interpolated between minimum and maximum values.
    """

    def get_dt(self) -> float:
        """
        :return: The signed change in value.
        """

        dt: float = abs(self._true_dt)
        if self._increase:
            return dt
        else:
            return -dt

    def _lerp(self) -> float:
        return TDWUtils.lerp(self._a, self._b, self._t)

    def _copy(self, v: float) -> float:
        return v

    def _set_increase(self) -> None:
        if self._a < self._b:
            self._increase = True
            self._t = 0
        else:
            self._increase = False
            temp = self._b
            self._b = self._a
            self._a = temp
            self._t = 1
