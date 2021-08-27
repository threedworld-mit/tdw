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

This tutorial will define an L-shaped scene with interior walls.

To start, we'll define the bounds of the room with a randomly-sized numpy array, where 0 = no walls, 1 = exterior walls, and 2 = interior walls:

```python
from typing import List
import numpy as np
from tdw.controller import Controller

class ProcGenRoom(Controller):
    def __init__(self, port: int = 1071, launch_build: bool = True, seed: int = 0):
        super().__init__(port=port, launch_build=launch_build)
        self.rng: np.random.RandomState = np.random.RandomState(seed)

    def create_scene(self) -> List[dict]:
        width: int = self.rng.randint(12, 18)
        length: int = self.rng.randint(14, 20)
        room_arr: np.array = np.zeros(shape=(width, length), dtype=int)
```

Define a position to start turning south and generate "walls" up to that point:

```python
from typing import List
import numpy as np
from tdw.controller import Controller

class ProcGenRoom(Controller):
    def __init__(self, port: int = 1071, launch_build: bool = True, seed: int = 0):
        super().__init__(port=port, launch_build=launch_build)
        self.rng: np.random.RandomState = np.random.RandomState(seed)

    def create_scene(self) -> List[dict]:
        width: int = self.rng.randint(12, 18)
        length: int = self.rng.randint(14, 20)
        room_arr: np.array = np.zeros(shape=(width, length), dtype=int)
        # Define the uppermost width-wise wall.
        turn_south_at = int(length * 0.75) + self.rng.randint(1, 3)
        for i in range(turn_south_at + 1):
            room_arr[0, i] = 1
        print(room_arr)
```

Output:

```
[[1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]]
```

Using similar logic, define the rest of the L-shape:

```python
from typing import List
import numpy as np
from tdw.controller import Controller

class ProcGenRoom(Controller):
    def __init__(self, port: int = 1071, launch_build: bool = True, seed: int = 0):
        super().__init__(port=port, launch_build=launch_build)
        self.rng: np.random.RandomState = np.random.RandomState(seed)

    def create_scene(self) -> List[dict]:
        width: int = self.rng.randint(12, 18)
        length: int = self.rng.randint(14, 20)
        room_arr: np.array = np.zeros(shape=(width, length), dtype=int)
        # Define the uppermost width-wise wall.
        turn_south_at = int(length * 0.75) + self.rng.randint(1, 3)
        for i in range(turn_south_at + 1):
            room_arr[0, i] = 1
        turn_west_at = int(width * 0.75) + self.rng.randint(0, 2)
        for i in range(turn_west_at + 1):
            room_arr[i, turn_south_at] = 1
        turn_north_at = turn_south_at - self.rng.randint(4, 6)
        for i in range(turn_north_at, turn_south_at):
            room_arr[turn_west_at, i] = 1
        turn_west_at_2 = self.rng.randint(4, 6)
        for i in range(turn_west_at_2, turn_west_at):
            room_arr[i, turn_north_at] = 1
        for i in range(turn_north_at):
            room_arr[turn_west_at_2, i] = 1
        for i in range(turn_west_at_2):
            room_arr[i, 0] = 1
        print(room_arr)
```

Output:

```
[[1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 0 0]
 [1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0]
 [1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0]
 [1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0]
 [1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0]
 [1 1 1 1 1 1 1 1 1 1 1 0 0 0 0 1 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 1 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 1 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 1 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 1 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 1 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 1 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 1 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]]
```

Next, add interior walls at the corner of the L, leaving some space for an entryway:



***

Python API:

- [`TDWUtils.get_box(width, length)`](../../python/tdw_utils.md)

Command API:

- [`load_scene`](../../api/command_api.md#load_scene)
- [`create_exterior_walls`](../../api/command_api.md#create_exterior_walls)
- [`create_interior_walls`](../../api/command_api.md#create_interior_walls)