from pathlib import Path
from typing import List, Union
from json import dumps
from tdw.output_data import OutputData, LogMessage
from tdw.add_ons.add_on import AddOn


class Logger(AddOn):
    """
    Log every command sent to the build.

    ```python
    from tdw.controller import Controller
    from tdw.add_ons.logger import Logger

    c = Controller()
    logger = Logger(path="log.txt")
    c.add_ons.append(logger)
    # The logger add-on will log this command.
    c.communicate({"$type": "do_nothing"})
    c.communicate({"$type": "terminate"})
    ```

    The log file can be automatically re-loaded into another controller using the [`LogPlayback`](log_playback.md) add-on.
    """

    def __init__(self, path: Union[str, Path], overwrite: bool = True, log_commands_in_build: bool = False):
        """
        :param path: The path to the log file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html).
        :param overwrite: If True and a log file already exists at `path`, overwrite the file.
        :param log_commands_in_build: If True, the build will log every message received and every command executed in the [Player log](https://docs.unity3d.com/Manual/LogFiles.html).
        """

        super().__init__()
        # If True, the build will log every message received and every command executed in the Player log.
        self._log_commands_in_build: bool = log_commands_in_build
        # Get or create the playback file path.
        if isinstance(path, str):
            self._path: Path = Path(path)
        else:
            self._path: Path = path
        if not self._path.parent.exists():
            self._path.parent.mkdir(parents=True)
        # Remove an existing log file.
        if overwrite and self._path.exists():
            self._path.unlink()

    def on_send(self, resp: List[bytes]) -> None:
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            # Print a log message.
            if r_id == "logm":
                log = LogMessage(resp[i])
                print(f"[FROM BUILD] {log.get_message_type()} from {log.get_object_type()}: {log.get_message()}")

    def get_initialization_commands(self) -> List[dict]:
        commands = [{"$type": "send_log_messages"}]
        if self._log_commands_in_build:
            commands.append({"$type": "set_network_logging",
                             "value": True})
        return commands

    def before_send(self, commands: List[dict]) -> None:
        # Log the commands.
        with self._path.open("at", encoding="utf-8") as f:
            f.write(dumps(commands) + "\n")

    def reset(self, path: Union[str, Path], overwrite: bool = True) -> None:
        """
        Reset the logger.

        :param path: The path to the log file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html).
        :param overwrite: If True and a log file already exists at `path`, overwrite the file.
        """

        self.initialized = False
        # Get or create the playback file path.
        if isinstance(path, str):
            self._path = Path(path)
        else:
            self._path = path
        if not self._path.parent.exists():
            self._path.parent.mkdir(parents=True)
        # Delete an existing log.
        if overwrite and self._path.exists():
            self._path.unlink()
