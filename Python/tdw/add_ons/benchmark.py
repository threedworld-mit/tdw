from time import time
from typing import List
from tdw.add_ons.add_on import AddOn


class Benchmark(AddOn):
    """
    Benchmark the FPS over a given number of frames.

    ```python
    from tdw.controller import Controller
    from tdw.add_ons.benchmark import Benchmark

    c = Controller()
    b = Benchmark(num_frames=2000)
    c.modules.append(b)
    while b.fps < 0:
        c.communicate([])
    c.communicate({"$type": "terminate"})
    ```
    """

    def __init__(self, num_frames: int):
        """
        :param num_frames: The number of frames over which to benchmark.
        """

        super().__init__()
        self.initialized = True
        # The current frame.
        self._frame: int = 0
        # The total number of frames.
        self._num_frames: int = num_frames
        # Total time elapsed.
        self._times: float = 0
        """:field
        The average frames per second.
        """
        self.fps: float = -1
        self._t0 = time()

    def get_initialization_commands(self) -> List[dict]:
        return[]

    def on_communicate(self, resp: List[bytes], commands: List[dict]) -> None:
        # We're done benchmarking.
        if self._frame >= self._num_frames:
            return
        self._frame += 1
        t1 = time()
        self._times += t1 - self._t0
        self._t0 = t1
        if self._frame >= self._num_frames:
            self.fps = self._num_frames / self._times
            print(self.fps)
