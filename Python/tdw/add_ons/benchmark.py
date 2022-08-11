from time import time
from typing import List
from tdw.add_ons.add_on import AddOn


class Benchmark(AddOn):
    """
    Benchmark the frames per second (FPS) over a given number of frames.
    """

    def __init__(self):
        """
        (no parameters)
        """

        super().__init__()
        self.initialized = True
        """:field
        A list of time elapsed per `communicate()` call.
        """
        self.times: List[float] = list()
        # If True, we are currently benchmarking.
        self._benchmarking: bool = False
        # The initial time.
        self._t0: float = -1
        """:field
        The frames per second of the previous benchmark test.
        """
        self.fps: float = -1

    def get_initialization_commands(self) -> List[dict]:
        """
        This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

        :return: A list of commands that will initialize this add-on.
        """

        return []

    def before_send(self, commands: List[dict]) -> None:
        """
        Update the time.

        :param commands: The commands that are about to be sent to the build.
        """

        if self._benchmarking:
            self._t0 = time()

    def on_send(self, resp: List[bytes]) -> None:
        """
        This is called after commands are sent to the build and a response is received.

        Use this function to send commands to the build on the next frame, given the `resp` response.
        Any commands in the `self.commands` list will be sent on the next frame.

        :param resp: The response from the build.
        """

        # Clock the benchmark.
        if self._benchmarking:
            t1 = time()
            self.times.append(t1 - self._t0)
            self._t0 = t1

    def start(self) -> None:
        """
        Start benchmarking each `communicate()` call and clear `self.times`.
        """

        self.fps = -1
        self.times.clear()
        self._benchmarking = True

    def stop(self) -> None:
        """
        Stop benchmarking each `communicate()` call and set `self.fps`.
        """

        self._benchmarking = False
        self.fps = len(self.times) / sum(self.times)
