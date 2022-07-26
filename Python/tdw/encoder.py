from json import JSONEncoder
from enum import Enum
from base64 import b64encode
import numpy as np


class Encoder(JSONEncoder):
    """
    Encode TDW classes into dictionaries that can then be dumped as JSON data.

    Minimal example:

    ```python
    from tdw.controller import Controller
    from tdw.tdw_utils import TDWUtils
    from tdw.add_ons.robot import Robot
    from tdw.encoder import Encoder


    c = Controller()
    robot = Robot(name="ur5")
    c.add_ons.append(robot)
    c.communicate(TDWUtils.create_empty_room(12, 12))
    encoder = Encoder()
    print(encoder.encode(robot))
    c.communicate({"$type": "terminate"})
    ```

    To save this dictionary to disk, use `json.dumps` as you would with any other JSON dictionary:

    ```python
    import json
    from tdw.controller import Controller
    from tdw.tdw_utils import TDWUtils
    from tdw.add_ons.robot import Robot
    from tdw.encoder import Encoder


    c = Controller()
    robot = Robot(name="ur5")
    c.add_ons.append(robot)
    c.communicate(TDWUtils.create_empty_room(12, 12))
    encoder = Encoder()

    # Encode the `Robot` to a dictionary.
    robot_data = encoder.encode(robot)
    # Dump the dictionary as a string.
    robot_string = json.dumps(robot_data, indent=2)
    # Write the string to disk.
    with open("robot_data.txt", "wt") as f:
        f.write(robot_string)
    c.communicate({"$type": "terminate"})
    ```

    Note that TDW does not provide a means of automatically converting dictionaries back into objects.
    """

    """:class_var
    If True, include hidden fields i.e. fields that begin with the `_` prefix. For some classes, such as `PyImpact`, this will include a lot of extraneous information.
    """
    INCLUDE_HIDDEN_FIELDS: bool = True

    def default(self, obj):
        """
        This is called internally. Use `Encoder().encode(obj)` instead.

        :param obj: The object.

        :return: A dictionary.
        """

        if isinstance(obj, Enum):
            return obj.name
        elif isinstance(obj, np.ndarray):
            # This is a 0-d array.
            if obj.shape == ():
                if obj.dtype == np.float32 or obj.dtype == float:
                    return float(obj)
                elif obj.dtype == np.int32 or obj.dtype == int:
                    return int(obj)
                elif obj.dtype == bool:
                    return bool(obj)
                else:
                    raise Exception(f"Not implemented: {obj.dtype}")
            # This is an n-d array.
            else:
                if obj.dtype == np.float32 or obj.dtype == float:
                    return [float(v) for v in obj]
                elif obj.dtype == np.int32 or obj.dtype == int:
                    return [int(v) for v in obj]
                elif obj.dtype == bool:
                    return [v for v in obj]
                else:
                    raise Exception(f"Not implemented: {obj.dtype}")
        # Ignore `RandomState` objects.
        elif isinstance(obj, np.random.RandomState):
            return None
        # Encode byte arrays to base64 strings.
        elif isinstance(obj, bytes):
            return b64encode(obj).decode("ascii")
        elif isinstance(obj, np.bool_):
            return bool(obj)
        else:
            # Include hidden fields.
            if Encoder.INCLUDE_HIDDEN_FIELDS:
                d = {k: v for k, v in obj.__dict__.items()}
            # Ignore hidden fields.
            else:
                d = {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
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
