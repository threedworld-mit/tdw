from pathlib import Path
from typing import List, Union
from json import loads
from tdw.add_ons.add_on import AddOn


class LogPlayback(AddOn):
    """
    Load and play back commands that were logged by a [`Logger`](logger.md) add-on.
    """

    def __init__(self):
        """
        (no arguments)
        """
        
        super().__init__()
        # We don't want to wait a frame to start sending commands, so this is always initialized.
        self.initialized = True
        """:field
        A list of lists of commands. Each list of commands is from a `communicate()` call from a prior controller, and will be sent per `communicate()` call to the current controller.
        """
        self.playback: List[List[dict]] = list()

    def load(self, path: Union[str, Path]) -> None:
        """
        Load a log file. This will deserialize all of the commands in the log file and add each list of commands to `self.record`. Per `communicate()` call (i.e. when `on_send(resp)` is invoked), this add-on will pop the first list of commands and add it to `self.commands`; in other words, it will send each list of commands exactly as they were sent when they were logged.

        :param path: The path to the log file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html).
        """

        # Get or create the playback file path.
        if isinstance(path, str):
            p: Path = Path(path)
        else:
            p: Path = path
        assert p.exists(), f"Log not found: {p}"
        # Open the file. Strip the file of empty lines. Remove Windows line breaks. Split along line breaks.
        for commands_text in p.read_text(encoding="utf-8").strip().replace("\r", "").split("\n"):
            # Deserialize the list of commands and append it.
            self.playback.append(loads(commands_text))

    def get_initialization_commands(self) -> List[dict]:
        return []

    def on_send(self, resp: List[bytes]) -> None:
        # Send the next list of commands.
        if len(self.playback) > 0:
            self.commands.extend(self.playback.pop(0))
