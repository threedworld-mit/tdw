from abc import ABC, abstractmethod
from typing import Generic, TypeVar
import numpy as np


T = TypeVar("T")


class Lerpable(Generic[T], ABC):
    """
    A value of type T that can be linearly interpolated between minimum and maximum values.
    """

    def __init__(self, value: T):
        """
        :param value: The initial value.
        """

        """:field
        The current value.
        """
        self.v: T = self._copy(value)
        # The minimum value.
        self._a: T = self._copy(value)
        # The maximum value.
        self._b: T = self._copy(value)
        # The change in `self._t` per `update()` call.
        self._dt: float = 0
        """:field
        If True, `self.v` is at its target (the minimum if increasing, the maximum if decreasing).
        """
        self.is_at_target: bool = True
        # The current t value on the line between `self._a` and `self._b`.
        self._t: float = 0
        # If True, increment `self._t` per `update()` call. If False, decrement.
        self._increase: bool = True

    def update(self) -> None:
        """
        Interpolate. If we're done interpolating, stop.

        This will set `self.v` to a value between the minimum and maximum.
        """

        if self.is_at_target:
            return
        # Increment the t value.
        if self._increase:
            self._t += self._dt
            if self._t >= 1:
                self._t = 1
                self.is_at_target = True
        else:
            self._t -= self._dt
            if self._t <= 0:
                self._t = 0
                self.is_at_target = True
        # Lerp.
        self.v = self._lerp()

    def set_target(self, target: T, dt: float) -> None:
        """
        Set a new target for `self.v`.

        One end of the line between a and b will be `self.v` and the other will be `target`.

        :param target: The target value.
        :param dt: The *true* value delta per `update()` call. For example, if this is a position and you want move the position by 0.1 meters per `update()` call, then this value should be 0.1.
        """

        self._a = self.v
        self._b = target
        if self._a < self._b:
            self._increase = True
            self._t = 0
        else:
            self._increase = False
            temp = self._b
            self._b = self._a
            self._a = temp
            self._t = 1
        # Convert the time delta to a value between 0 and 1.
        self._dt = abs(dt) / np.linalg.norm(self._b - self._a)
        self.is_at_target = False

    @abstractmethod
    def _lerp(self) -> T:
        """
        :return: A new value for `self.v` that is between `self._a` and `self._b` at point `self._t`.
        """

        raise Exception()

    @abstractmethod
    def _copy(self, v: T) -> T:
        """
        :param v: A value.

        :return: A copy of `v`.
        """

        raise Exception()
