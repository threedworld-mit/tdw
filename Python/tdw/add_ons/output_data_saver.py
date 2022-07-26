from base64 import b64encode, b64decode
from json import loads, dumps
from typing import List, Union
from pathlib import Path
from tdw.add_ons.add_on import AddOn


class OutputDataSaver(AddOn):
    """
    Save raw output byte data to disk per frame. This data is encoded into base64 strings and saved as text files.
    """

    def __init__(self, output_directory: Union[str, Path], zero_padding: int = 8):
        """
        :param output_directory: The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this doesn't exist, it will be created.
        :param zero_padding: How many zeros to append to the file name. By default, the name of the file of the first frame will be `00000000.txt`.
        """

        super().__init__()
        self._zero_padding: int = zero_padding
        self.initialized = True
        if isinstance(output_directory, str):
            """:field
            The root output directory as a [`Path`](https://docs.python.org/3/library/pathlib.html). If this doesn't exist, it will be created.
            """
            self.output_directory: Path = Path(output_directory)
        elif isinstance(output_directory, Path):
            self.output_directory = output_directory
        else:
            raise Exception(output_directory)
        if not self.output_directory.exists():
            self.output_directory.mkdir(parents=True)
        self._frame_count: int = 0

    def get_initialization_commands(self) -> List[dict]:
        return []

    def on_send(self, resp: List[bytes]) -> None:
        # Encode `resp` to base64 and save it to a file named after the frame number.
        self._get_path(self._frame_count).write_text(dumps([b64encode(r).decode("ascii") for r in resp]))
        self._frame_count += 1

    def read(self, frame_number: int) -> List[bytes]:
        """
        Read saved ouput data.

        :param frame_number: The frame number. This gets appended to `self.output_directory` with zero-padding to create the full file path, e.g. `output_directory/00000000.txt`.

        :return: A list of bytes that was saved as base64 data, equivalent to the return value of a `c.communicate(commands)` call (i.e. `resp` as it usually appears in our example controllers).
        """

        return [b64decode(r) for r in loads(self._get_path(frame_number).read_text())]

    def reset(self) -> None:
        """
        This will reset the frame count.
        """

        self._frame_count = 0

    def _get_path(self, frame_number: int) -> Path:
        """
        :param frame_number: The frame number.

        :return: A file path from `self.output_directory`.
        """

        return self.output_directory.joinpath(str(frame_number).zfill(self._zero_padding) + ".txt")
