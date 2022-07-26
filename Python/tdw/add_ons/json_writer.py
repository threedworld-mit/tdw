from json import dumps
from typing import List, Union, Dict
from pathlib import Path
from tdw.add_ons.writer import Writer
from tdw.backend.encoder import Encoder


class JsonWriter(Writer):
    def __init__(self, objects: Dict[str, object], output_directory: Union[str, Path], indent: int = 2,
                 include_hidden_fields: bool = True, zero_padding: int = 8):
        """
        :param objects: A dictionary of objects to serialize. Key = A name or identifier for the object, for example `"robot"`. Value = A data object, for example a [`Robot`](robot.md).
        :param output_directory: The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this doesn't exist, it will be created.
        :param indent: The indentation level of the output JSON strings.
        :param include_hidden_fields: If True, include hidden fields in the JSON data i.e. any fields which have names that begin with `_`. This will give you *all* of the data, but often you won't want this. Many TDW classes hold megabytes of data in hidden fields, which is trivial to do in memory but serializing this data can be very slow.
        :param zero_padding: How many zeros to append to the file name. By default, the name of the file of the first frame will be `00000000.txt`.
        """

        super().__init__(output_directory=output_directory, zero_padding=zero_padding)
        Encoder.INCLUDE_HIDDEN_FIELDS = include_hidden_fields
        self.objects: Dict[str, object] = objects
        self._encoder: Encoder = Encoder()
        self._indent: int = indent

    def on_send(self, resp: List[bytes]) -> None:
        for name in self.objects:
            path = self.output_directory.joinpath(f"{name}_{str(self._frame_count).zfill(self._zero_padding)}.json")
            path.write_text(dumps(self._encoder.encode(self.objects[name]), indent=self._indent), encoding="utf-8")
        self._frame_count += 1
