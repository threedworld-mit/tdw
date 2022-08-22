from abc import ABC, abstractmethod
from typing import List, Union, TypeVar, Generic
from pathlib import Path
from overrides import final
from tdw.add_ons.add_on import AddOn


T = TypeVar("T")


class Writer(AddOn, Generic[T], ABC):
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

    @abstractmethod
    def read(self, path: Union[str, Path, int]) -> T:
        """
        Read saved ouput data.

        :param path: The path to the frame file. This can be a string or [`Path`](https://docs.python.org/3/library/pathlib.html) file path or an integer. If this is an integer, it represents the frame number; the file is assumed to be in `self.output_directory`.

        :return: Deserialized data.
        """

        raise Exception()
