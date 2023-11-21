from base64 import b64encode, b64decode
from json import loads, dumps
from typing import List, Union
from pathlib import Path
from zipfile import ZipFile
from tdw.add_ons.writer import Writer
from tdw.tdw_utils import TDWUtils


class OutputDataWriter(Writer[List[bytes]]):
    """
    Save raw output byte data to disk per frame. This data is encoded into base64 strings and saved as text files.
    """

    def __init__(self, output_directory: Union[str, Path], zero_padding: int = 8, zip_filename: str = None):
        """
        :param output_directory: The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this doesn't exist, it will be created.
        :param zero_padding: How many zeros to append to the file name. By default, the name of the file of the first frame will be `00000000.txt`.
        :param zip_filename: If not None, this is the name of a .zip file in `output_directory`. Data will be added to this .zip file instead of being written as separate files.
        """

        super().__init__(output_directory=output_directory, zero_padding=zero_padding)
        if zip_filename is not None:
            self._zip_path: str = str(TDWUtils.get_path(self.output_directory).joinpath(zip_filename).resolve())
            self._zip: bool = True
        else:
            self._zip_path = ""
            self._zip = False

    def on_send(self, resp: List[bytes]) -> None:
        # Append to a zip file.
        if self._zip:
            # Flatten the output data.
            bs: bytearray = bytearray()
            # Add the number of elements.
            bs.extend(len(resp).to_bytes(4, byteorder="little"))
            # Add the lengths of each element.
            for i in range(len(resp)):
                bs.extend(len(resp[i]).to_bytes(4, byteorder="little"))
            # Add each frame.
            for i in range(len(resp)):
                bs.extend(resp[i])
            with ZipFile(self._zip_path, "a") as z:
                # Create the file.
                z.writestr(str(self._frame_count).zfill(self._zero_padding), bytes(bs))
        # Encode `resp` to base64 and save it to a file named after the frame number.
        else:
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
