from base64 import b64encode, b64decode
from json import loads, dumps
from typing import List, Union
from pathlib import Path
from tdw.add_ons.writer import Writer


class OutputDataWriter(Writer[List[bytes]]):
    """
    Save raw output byte data to disk per frame. This data is encoded into base64 strings and saved as text files.
    """

    def on_send(self, resp: List[bytes]) -> None:
        # Encode `resp` to base64 and save it to a file named after the frame number.
        self._get_path(self._frame_count).write_text(dumps([b64encode(r).decode("ascii") for r in resp]))
        self._frame_count += 1

    def read(self, path: Union[str, Path, int]) -> List[bytes]:
        """
        Read saved ouput data.

        :param path: The path to the frame file. This can be a string or [`Path`](https://docs.python.org/3/library/pathlib.html) file path or an integer. If this is an integer, it represents the frame number; the file is assumed to be in `self.output_directory`.

        :return: A list of bytes that was saved as base64 data, equivalent to the return value of a `c.communicate(commands)` call (i.e. `resp` as it usually appears in our example controllers).
        """

        if isinstance(path, str):
            text = Path(path).read_text()
        elif isinstance(path, Path):
            text = path.read_text()
        elif isinstance(path, int):
            text = self._get_path(path).read_text()
        else:
            raise Exception(path)
        return [b64decode(r) for r in loads(text)]

    def _get_path(self, frame_number: int) -> Path:
        """
        :param frame_number: The frame number.

        :return: A file path from `self.output_directory`.
        """

        return self.output_directory.joinpath(str(frame_number).zfill(self._zero_padding) + ".txt")
