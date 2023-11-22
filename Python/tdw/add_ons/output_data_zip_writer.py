from typing import List, Union
from pathlib import Path
from zipfile import ZipFile
from tdw.add_ons.writer import Writer
from tdw.tdw_utils import TDWUtils


class OutputDataZipWriter(Writer[List[List[bytes]]]):
    """
    Save raw output byte data to disk in a .zip file.
    """

    def __init__(self, output_path: Union[str, Path], zero_padding: int = 8):
        """
        :param output_path: The .zip file path a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If the parent directory doesn't exist, it will be created.
        :param zero_padding: How many zeros to append to the file name. By default, the name of the file of the first frame will be `00000000.txt`.
        """

        super().__init__(output_directory=output_path.parent, zero_padding=zero_padding)
        self._zip_path: str = str(TDWUtils.get_path(output_path))

    def on_send(self, resp: List[bytes]) -> None:
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
        self._frame_count += 1

    def read(self, path: Union[str, Path]) -> List[List[bytes]]:
        """
        Read saved ouput data.

        :param path: The path to the .zip file. This can be a string or [`Path`](https://docs.python.org/3/library/pathlib.html) file path.

        :return: A list of bytes, equivalent to each return value of each `c.communicate(commands)` call (i.e. `resp` as it usually appears in our example controllers).
        """

        resps: List[List[bytes]] = list()
        with ZipFile(TDWUtils.get_string_path(path), "r") as z:
            for f in z.filelist:
                # Open the byte array.
                bs: bytes = z.open(f).read()
                resp: List[bytes] = list()
                # Get the number of frames in `resp`.
                num_frames: int = int.from_bytes(bs[0:4], byteorder="little")
                nums_offset: int = 4 + num_frames * 4
                frame_offset: int = nums_offset
                for i in range(num_frames):
                    # Get the length of this frame.
                    frame_length: int = int.from_bytes(bs[4 * (i + 1): (4 * (i + 1) + 4)], byteorder="little")
                    # Get the frame slice and add it to `resp`.
                    resp.append(bs[frame_offset: frame_offset + frame_length])
                    frame_offset += frame_length
                resps.append(resp)
        return resps
