# `floorplan_controller.py`

## `FloorplanController(Controller)`

`from tdw.floorplan_controller import FloorplanController`

A controller that can create an interior scene populated with objects.

```python
from tdw.floorplan_controller import FloorplanController

c = FloorplanController()
init_commands = c.get_scene_init_commands(scene="2a", layout=0, audio=True)
c.communicate(init_commands)
```

***

#### `get_scene_init_commands(self, scene: str, layout: int, audio: bool) -> List[dict]`

Get commands to create a scene and populate it with objects.
Valid scenes and layouts:
| `scene` | `layout` |
| --- | --- |
| 2a, 2b, or 2c | 0, 1, or 2 |
| 4a, 4b, or 4c | 0, 1, or 2 |

| Parameter | Description |
| --- | --- |
| scene | The name of the scene. Corresponds to a record named: `floorplan_[scene]`. |
| layout | The layout index. |
| audio | If True, instantiate physics values per object from audio properties. |

_Returns:_  A list of commands to initialize the scene and populate it with objects.

***

