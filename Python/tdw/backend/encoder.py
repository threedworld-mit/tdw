from json import JSONEncoder
from enum import Enum
from base64 import b64encode
from pathlib import Path
import numpy as np
from inflection import underscore


class Encoder(JSONEncoder):
    """
    Encode TDW classes into dictionaries that can then be dumped as JSON data.
    """

    """:class_var
    If True, include hidden fields i.e. fields that begin with the `_` prefix. For some classes, this will include a lot of extraneous information.
    """
    INCLUDE_HIDDEN_FIELDS: bool = False

    def default(self, obj):
        """
        This is called internally. Use `Encoder().encode(obj)` instead.

        :param obj: The object.

        :return: A dictionary.
        """

        if isinstance(obj, Enum):
            return obj.name
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        # Ignore `RandomState` objects.
        elif isinstance(obj, np.random.RandomState):
            return None
        elif isinstance(obj, np.bool_):
            return bool(obj)
        # Encode byte arrays to base64 strings.
        elif isinstance(obj, bytes) or isinstance(obj, bytearray):
            return b64encode(obj).decode("ascii")
        # Convert Path objects to absolute file path strings.
        elif isinstance(obj, Path):
            return str(obj.resolve()).replace("\\", "/")
        else:
            try:
                # Include the type identifier.
                if 'tdw' in obj.__class__.__module__ and obj.__class__.__name__ != "TrialMessage":
                    d: dict = {"$type": underscore(obj.__class__.__name__)}
                else:
                    d = dict()
                # Include hidden fields.
                if Encoder.INCLUDE_HIDDEN_FIELDS:
                    d.update({k: v for k, v in obj.__dict__.items()})
                # Ignore hidden fields.
                else:
                    d.update({k: v for k, v in obj.__dict__.items() if not k.startswith("_")})
            # Flatbuffer objects don't have dictionaries.
            except AttributeError as e:
                print("JSON encoding error:", e)
                return None
            # Convert non-serializable keys to string.
            for k in d:
                if isinstance(d[k], dict):
                    temp = dict()
                    for q in d[k]:
                        if isinstance(q, Enum):
                            temp[q.name] = d[k][q]
                        elif isinstance(q, str):
                            temp[q] = d[k][q]
                        else:
                            temp[str(q)] = d[k][q]
                    d[k] = temp
            return d
