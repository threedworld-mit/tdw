from abc import ABC
from typing import List, Union
from pathlib import Path
from overrides import final
from tdw.add_ons.add_on import AddOn


class Writer(AddOn, ABC):
    """
    Abstract base class for per-frame data writers.
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
    
    @final
    def get_initialization_commands(self) -> List[dict]:
        return []

    @final
    def reset(self) -> None:
        """
        This will reset the frame count.
        """

        self._frame_count = 0
