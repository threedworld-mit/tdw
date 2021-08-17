# The `_mask` pass

The `_mask` pass is similar to the `_id` and `_category` passes but all objects are the same color:

![](images/mask_0000.png)

## `Occlusion` output data

It is possible to use the `_mask` pass to determine to what extent environment objects such as walls are occluding the objects. However, this can be a slow process on the Python controller end. TDW includes [`Occlusion`](../../api/output_data.md#Occlusion.md) data that simplifies and greatly speeds up the process. 

Internally, the build will capture two `_mask` passes, one with environment objects and one without. The resulting occlusion value is the ratio of the overall grayscale values of the images:

```python
from typing import List
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData
from tdw.output_data import Occlusion as Occl

"""
Use occlusion data to measure to what extent objects in the scene are occluded.
"""


class Occlusion(Controller):
    def run(self) -> None:
        """
        Create a scene with a row of objects and an avatar.
        Get occlusion data.
        Put a wall in front of the objects and get occlusion data again.
        """

        # Create the scene.
        commands = [{"$type": "load_scene",
                     "scene_name": "ProcGenScene"},
                    TDWUtils.create_empty_room(12, 12)]
        # Add some objects.
        x = -2
        for i in range(5):
            commands.append(self.get_add_object(object_id=i,
                                                model_name="iron_box",
                                                position={"x": x, "y": 0, "z": 0}))
            x += 0.66
        # Add an avatar.
        commands.extend(TDWUtils.create_avatar(position={"x": 2, "y": 0.9, "z": 0.88},
                                               look_at=TDWUtils.VECTOR3_ZERO))
        # Request Occlusion output data per frame.
        commands.append({"$type": "send_occlusion",
                         "frequency": "once"})
        resp = self.communicate(commands)
        self.parse_resp(resp=resp)

        # Treat some of the objects as occluders.
        resp = self.communicate({"$type": "send_occlusion",
                                 "frequency": "once",
                                 "object_ids": [2, 4, 5]})
        self.parse_resp(resp=resp)

        # Place a wall in front of all of the objects.
        resp = self.communicate([{"$type": "send_occlusion",
                                  "frequency": "once"},
                                 {"$type": "create_interior_walls",
                                  "walls": [{"x": 7, "y": 5}, {"x": 7, "y": 6}]}])
        self.parse_resp(resp=resp)
        self.communicate({"$type": "terminate"})

    @staticmethod
    def parse_resp(resp: List[bytes]) -> None:
        """
        Parse the output data and print the occlusion.

        :param resp: The response from the build.
        """

        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "occl":
                occl = Occl(resp[i])
                print(occl.get_occluded())


if __name__ == "__main__":
    c = Occlusion(launch_build=False)
    c.run()
```

Result:

```
0.0
0.375
0.625
```

***

**Next: [The `_normals` pass](normals.md)**

Example controllers:

- [occlusion.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/capture_passes/occlusion.py) Example implementation of `Occlusion` output data.

Command API:

- [`send_occlusion`](../../api/command_api.md#send_occlusion)

Output Data API:

- [`Occlusion`](../../api/output_data.md#Occlusion.md)
