##### Objects and Scenes

# Procedural generation (scenes)

Having reviewed [TDW's built-in system for scripted object placement](floorplans.md), the rest of this tutorial will cover how to procedurally generate environments.

TDW includes a "ProcGen Room" scene for procedurally generating interior environments. We've been utilizing this every time we call `TDWUtils.create_empty_room(12, 12)`. However, TDW is capable of generating arbitrary indoor environments, with the caveat that each "section" of wall is always 1 meter long and walls must always be at 90 degree angles.

## 1. Create a random number generator

It can be useful to define a random number generator with a fixed seed so that you can re-create the exact same scene as needed:

```python
from typing import List
import numpy as np
from tdw.controller import Controller

class ProcGenRoom(Controller):
    def __init__(self, port: int = 1071, launch_build: bool = True, seed: int = 0):
        super().__init__(port=port, launch_build=launch_build)
        self.rng: np.random.RandomState = np.random.RandomState(seed)
```

## 2. Procedurally generate the walls of an indoor scene

To start, we'll use a different wrapper function, [`TDWUtils.get_box(width, length)`](../../python/tdw_utils.md) to generate a box-shaped scene of exterior walls:

```python
from typing import List
import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

class ProcGenRoom(Controller):
    def __init__(self, port: int = 1071, launch_build: bool = True, seed: int = 0):
        super().__init__(port=port, launch_build=launch_build)
        self.rng: np.random.RandomState = np.random.RandomState(seed)

    def create_scene(self) -> List[dict]:
        # Typically, load_scene is sent when we call c.start()
        commands = [{"$type": "load_scene",
                     "scene_name": "ProcGenScene"}]
        # Randomly set the dimensions of the scene.
        width: int = self.rng.randint(10, 16)
        length: int = self.rng.randint(20, 30)
        # Create the exterior walls.
        exterior_walls = TDWUtils.get_box(width, length)
        commands.append({"$type": "create_exterior_walls",
                         "walls": exterior_walls})
```



***

Python API:

- [`TDWUtils.get_box(width, length)`](../../python/tdw_utils.md)

Command API:

- [`load_scene`](../../api/command_api.md#load_scene)
- [`create_exterior_walls`](../../api/command_api.md#create_exterior_walls)
- [`create_interior_walls`](../../api/command_api.md#create_interior_walls)