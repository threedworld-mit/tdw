from json import dumps, loads
from typing import List, Union, Dict
from pathlib import Path
from tdw.add_ons.writer import Writer
from tdw.backend.encoder import Encoder


class JsonWriter(Writer[Union[dict, Dict[str, dict]]]):
    """
    Dump JSON data of objects per-frame. *Objects* in this case refers not to TDW objects but to Python objects, such as a [`Robot`](robot.md) add-on or an arbitrary dictionary of data.

    Per frame, these objects will be read, encoded into Python dictionaries, and written out as serialized JSON data files.

    The JSON files can be read and reloaded like any other file with JSON information. However, TDW does not provide a means of automatically converting serialized JSON data back into objects.

    Data is converted to JSON-serializable format as follows:

    - Numpy arrays are converted to Python lists.
    - Numpy `RandomState` objects, which many TDW classes use, are not serialized and receive a null value.
    - `bytes` and `bytearray` objects are converted into base64 strings.
    - [`Path`](https://docs.python.org/3/library/pathlib.html) objects are converted into absolute filepath strings.
    - Some classes, namely those in the `tdw.FBOutput` namespace, can't readily be serialized to a dictionary; their values are instead set to null.
    - Enum values are converted to their string representation i.e. `value.name`.
    - Dictionaries that have non-string keys have all of their keys converted into strings i.e. `str(key)`.
    """

    def __init__(self, objects: Dict[str, object], output_directory: Union[str, Path], indent: int = 2,
                 include_hidden_fields: bool = False, zero_padding: int = 8):
        """
        :param objects: A dictionary of objects to serialize. Key = A name or identifier for the object, for example `"robot"`. Value = A data object, for example a [`Robot`](robot.md).
        :param output_directory: The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this doesn't exist, it will be created.
        :param indent: The indentation level of the output JSON strings.
        :param include_hidden_fields: If True, include hidden fields in the JSON data i.e. any fields which have names that begin with `_`. This will give you *all* of the data, but often you won't want this. Many TDW classes hold megabytes of data in hidden fields, which is trivial to do in memory but serializing this data can be very slow.
        :param zero_padding: How many zeros to append to the file name. By default, the name of the file of the first frame will be `00000000.txt`.
        """

        super().__init__(output_directory=output_directory, zero_padding=zero_padding)
        # Set the hidden fields class variable.
        Encoder.INCLUDE_HIDDEN_FIELDS = include_hidden_fields
        """:field
        A dictionary of objects to serialize. Key = A name or identifier for the object, for example `"robot"`. Value = A data object, for example a [`Robot`](robot.md).
        """
        self.objects: Dict[str, object] = objects
        self._encoder: Encoder = Encoder()
        self._indent: int = indent

    def on_send(self, resp: List[bytes]) -> None:
        for name in self.objects:
            self._get_path(name=name, frame_number=self._frame_count).write_text(dumps(self._encoder.encode(self.objects[name]),
                                                                                       indent=self._indent),
                                                                                 encoding="utf-8")
        self._frame_count += 1

    def read(self, path: Union[str, Path, int]) -> Union[dict, Dict[str, dict]]:
        """
        Read saved ouput data.

        :param path: The path to the frame file. This can be a string or [`Path`](https://docs.python.org/3/library/pathlib.html) file path or an integer. If this is an integer, it represents the frame number; the file is assumed to be in `self.output_directory`.

        :return: If `path` is a string or a `Path`, this will return a dictionary. If `path` is an integer, this will return a *dictionary of dictionaries* where the key is the object name (e.g. `"robot"`) and the value is the corresponding dictionary.
        """

        if isinstance(path, str):
            return loads(Path(path).read_text(encoding="utf-8"))
        elif isinstance(path, Path):
            return loads(path.read_text(encoding="utf-8"))
        elif isinstance(path, int):
            data = dict()
            for name in self.objects:
                data[name] = loads(self._get_path(name=name, frame_number=path).read_text(encoding="utf-8"))
            return data
        else:
            raise Exception(path)

    def _get_path(self, name: str, frame_number: int) -> Path:
        """
        :param name: The object name.
        :param frame_number: The frame number

        :return: A file path from `self.output_directory`.
        """

        return self.output_directory.joinpath(f"{name}_{str(frame_number).zfill(self._zero_padding)}.json")
