from pathlib import Path
from typing import List, Union
from json import load, dump
from tdw.output_data import OutputData, LogMessage
from tdw.add_ons.add_on import AddOn


class Logger(AddOn):
    """
    Record and playback every command sent to the build.

    ```python
    from tdw.controller import Controller
    from tdw.add_ons.logger import Logger

    c = Controller()
    logger = Logger(record=True, path="log.json")
    c.add_ons.append(logger)
    # The logger add-on will log this command.
    c.communicate({"$type": "do_nothing"})
    # The logger add-on will log this command and generate a log.json file.
    c.communicate({"$type": "terminate"})
    ```
    """

    def __init__(self, record: bool, path: Union[str, Path], log_commands_in_build: bool = False):
        """
        :param record: If True, record each command. If False, play back an existing record.
        :param path: The path to either save the record to or load the record from.
        :param log_commands_in_build: If True, the build will log every message received and every command executed in the [Player log](https://docs.unity3d.com/Manual/LogFiles.html).
        """

        super().__init__()

        # If True, the build will log every message received and every command executed in the Player log.
        self._log_commands_in_build: bool = log_commands_in_build

        """:field
        If True, record each command. If False, play back an existing record.
        """
        self.record: bool = record

        # Get or create the playback file path.
        if isinstance(path, str):
            self._path: Path = Path(path)
        else:
            self._path: Path = path
        if not self._path.parent.exists():
            self._path.parent.mkdir(parents=True)

        # Start a new playback file.
        if self.record:
            """:field
            A record of each list of commands sent to the build.
            """
            self.playback: List[List[dict]] = list()
        # Load an existing .json file.
        else:
            with self._path.open("rt", encoding="utf-8") as f:
                self.playback = load(f)

    def on_send(self, resp: List[bytes]) -> None:
        # Prepare to send the next list of commands.
        if not self.record:
            if len(self.playback) > 0:
                self.commands = self.playback.pop(0)
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            # Print a log message.
            if r_id == "logm":
                log = LogMessage(resp[i])
                print(f"[FROM BUILD] {log.get_message_type()} from {log.get_object_type()}: {log.get_message()}")
            # If we get a quit signal and we're recording, save the log file.
            elif r_id == "quit" and self.record:
                self.save()

    def get_initialization_commands(self) -> List[dict]:
        commands = [{"$type": "send_log_messages"}]
        if self._log_commands_in_build:
            commands.append({"$type": "set_network_logging",
                             "value": True})
        return commands

    def before_send(self, commands: List[dict]) -> None:
        # Record the commands that were just sent.
        if self.record:
            self.playback.append(commands[:])

    def save(self) -> None:
        """
        Write the record of commands sent to the local disk.
        """

        with self._path.open("wt", encoding="utf-8") as f:
            dump(self.playback, f)

    def reset(self, path: Union[str, Path]) -> None:
        """
        Reset the logger. If `self.record == True`, this starts a new log. If `self.record == False`, this loads a playback file.

        :param path: The path to either save the record to or load the record from.
        """

        self.initialized = False
        self.commands.clear()
        self.playback.clear()
        # Get or create the playback file path.
        if isinstance(path, str):
            self._path = Path(path)
        else:
            self._path = path
        if not self._path.parent.exists():
            self._path.parent.mkdir(parents=True)

        # Start a new playback file.
        if self.record:
            self.playback = list()
        # Load an existing .json file.
        else:
            with self._path.open("rt", encoding="utf-8") as f:
                self.playback = load(f)
