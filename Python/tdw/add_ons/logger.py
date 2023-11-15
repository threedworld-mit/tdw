from io import BytesIO
from zipfile import ZipFile
from pathlib import Path
from typing import List, Union
from json import dumps
from tdw.output_data import OutputData, LogMessage
from tdw.add_ons.add_on import AddOn
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils


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

    def __init__(self, path: Union[str, Path], overwrite: bool = True, log_commands_in_build: bool = False,
                 output_data: bool = False):
        """
        :param path: The path to the log file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html).
        :param overwrite: If True and a log file already exists at `path`, overwrite the file.
        :param log_commands_in_build: If True, the build will log every message received and every command executed in the [Player log](https://docs.unity3d.com/Manual/LogFiles.html).
        :param output_data: If True, write output data to disk.
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
        self._output_data: bool = output_data
        # Create the output data directory.
        self._output_data_directory: Path = self._path.parent.joinpath(self._path.stem + "_output_data")
        if self._output_data and not self._output_data_directory.exists():
            self._output_data_directory.mkdir(parents=True)

    def on_send(self, resp: List[bytes]) -> None:
        # Zip the data and write to disk.
        if self._output_data:
            zip_buffer: BytesIO = BytesIO()
            with ZipFile(zip_buffer, "w") as z:
                # Write each output data array as a separate file.
                for i in range(len(resp) - 1):
                    z.writestr(OutputData.get_data_type_id(resp[i]), resp[i])
            # Write to disk.
            self._output_data_directory.joinpath(f"{TDWUtils.zero_padding(Controller.get_frame(resp[-1]), 8)}.zip").write_bytes(zip_buffer.getvalue())
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
