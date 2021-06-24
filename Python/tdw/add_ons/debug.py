from pathlib import Path
from typing import List, Union
from json import load, dump
from tdw.output_data import OutputData, LogMessage
from tdw.add_ons.add_on import AddOn


class Debug(AddOn):
    """
    Use this module to record and playback every command sent to the build.
    """

    def __init__(self, record: bool, path: Union[str, Path]):
        """
        :param record: If True, record each command. If False, play back an existing record.
        :param path: The path to either save the record to or load the record from.
        """

        super().__init__()

        # We don't need to initialize anything.
        self.initialized = True

        """:field
        If True, record each command. If False, play back an existing record.
        """
        self.record: bool = record

        # Get or create the playback file path.
        if isinstance(path, str):
            self._path: Path = Path(path)
        else:
            self._path: Path = path
        if not self._path.parent.exists:
            self._path.parent.mkdir(parents=True)

        # Start a new playback file.
        if self.record:
            """:field
            A record of each list of commands sent to the build.
            """
            self.playback: List[List[dict]] = list()
        # Load an existing .json file.
        else:
            with path.open("rt", encoding="utf-8") as f:
                self.playback = load(f)

    def on_communicate(self, resp: List[bytes], commands: List[dict]) -> None:
        # Record the commands that were just sent.
        if self.record:
            self.playback.append(commands[:])
        # Prepare to send the next list of commands.
        else:
            if len(self.playback) > 0:
                self.commands = self.playback.pop(0)
        # Print any messages from the build.
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "logm":
                log = LogMessage(resp[i])
                print(f"[FROM BUILD] {log.get_message_type()} from {log.get_object_type()}: {log.get_message()}")

    def get_initialization_commands(self) -> List[dict]:
        return [{"$type": "send_log_messages"}]

    def save(self) -> None:
        """
        Write the record of commands sent to the local disk.
        """

        with self._path.open("wt", encoding="utf-8") as f:
            dump(self.playback, f)
