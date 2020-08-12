from tdw.controller import Controller
from json import dumps, load
import io
from typing import Union, List
from time import time


class DebugController(Controller):
    """
    DebugController is a subclass of Controller that records every list of commands sent to the build.
    You can "play back" these commands, i.e. re-send them to the build.
    You can also save all of the recorded commands to a local file.

        ```python
    from tdw.debug_controller import DebugController
    c = DebugController()
    c.start()
    ```
    """

    def __init__(self, port: int = 1071, launch_build: bool = True):
        """
        Create the network socket and bind the socket to the port.

        :param port: The port number.
        :param launch_build: If True, automatically launch the build. If one doesn't exist, download and extract the correct version. Set this to False to use your own build, or (if you are a backend developer) to use Unity Editor.
        """

        # This will be used to record each list of commands sent to the build.
        self.record = []

        super().__init__(port=port, launch_build=launch_build)

    def communicate(self, commands: Union[dict, List[dict]]) -> list:
        """
        Send commands and receive output data in response. Record the commands immediately prior to sending them.

        :param commands: A list of JSON commands.

        :return The output data from the build.
        """

        # Record the commands.
        self.record.append(commands)

        return super().communicate(commands)

    def playback(self, print_commands: bool = False) -> None:
        """
        Send the record of commands to the build.

        :param print_commands: If true, print each list of commands before it is sent.
        """

        playback_commands = self.record[:]
        for commands in playback_commands:
            if print_commands:
                print(commands)
            self.communicate(commands)

    def save_record(self, filepath: str) -> None:
        """
        Write the record of commands sent to the local disk.

        :param filepath: The absolute path to which the record will be written.
        """

        with open(filepath, "wb") as f:
            f.write(dumps(self.record).encode("utf-8"))

    def load_record(self, filepath: str) -> None:
        """
        If this controller was set to debug, load a record of commands from the local disk.

        :param filepath: The absolute path from which the record will be loaded.
        """

        with io.open(filepath, "rt", encoding="utf-8") as f:
            self.record = load(f)

    def get_benchmark(self, num_frames: int) -> float:
        """
        Calculate a frames per second (FPS) benchmark.
        Send an empty list of commands for a given number of frames.

        :param num_frames: The number of frames for which the benchmark test will run.

        :return The average FPS.
        """

        times: float = 0

        for i in range(num_frames):
            t0 = time()
            self.communicate([])
            times += time() - t0
        return num_frames / times

    def clear_playback_record(self) -> None:
        """
        Clear all recorded data from memory.
        Useful if you want the playback file to exclude previous commands (i.e. in a very long simulation).
        """

        self.record.clear()
