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

Using similar logic, we'll define the rest of the L-shape:

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

Next, add interior walls at the corner of the L, leaving some space for an entryway:

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
        # Create interior walls.
        if self.rng.random() < 0.5:
            interior_wall_0 = range(turn_north_at + 1, turn_south_at - 1)
            interior_wall_1 = range(1, turn_west_at_2 - 1)
        else:
            interior_wall_0 = range(turn_north_at + 2, turn_south_at)
            interior_wall_1 = range(2, turn_west_at_2)
        for i in interior_wall_0:
            room_arr[turn_west_at_2, i] = 2
        for i in interior_wall_1:
            room_arr[i, turn_north_at] = 2
        print(room_arr)
```

We now have completed the interior and exterior walls. We will convert the array into commands, add an avatar, and send the commands:

```python
from typing import List
import numpy as np
from tdw.controller import Controller
from tdw.add_ons.image_capture import ImageCapture
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


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
        # Create interior walls.
        if self.rng.random() < 0.5:
            interior_wall_0 = range(turn_north_at + 1, turn_south_at - 1)
            interior_wall_1 = range(1, turn_west_at_2 - 1)
        else:
            interior_wall_0 = range(turn_north_at + 2, turn_south_at)
            interior_wall_1 = range(2, turn_west_at_2)
        for i in interior_wall_0:
            room_arr[turn_west_at_2, i] = 2
        for i in interior_wall_1:
            room_arr[i, turn_north_at] = 2
        # Convert the array to commands.
        exterior_walls: List[dict] = list()
        interior_walls: List[dict] = list()
        for ix, iy in np.ndindex(room_arr.shape):
            if room_arr[ix, iy] == 1:
                exterior_walls.append({"x": ix, "y": iy})
            elif room_arr[ix, iy] == 2:
                interior_walls.append({"x": ix, "y": iy})
        # load_scene typically gets sent by calling c.start()
        return [{"$type": "load_scene",
                 "scene_name": "ProcGenScene"},
                {"$type": "create_exterior_walls",
                 "walls": exterior_walls},
                {"$type": "create_interior_walls",
                 "walls": interior_walls}]

    def run(self) -> None:
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("proc_gen_room")
        print(f"Images will be saved to {path}")
        camera = ThirdPersonCamera(avatar_id="a", position={"x": 0, "y": 20, "z": 0}, look_at={"x": 0, "y": 0, "z": 0})
        capture = ImageCapture(avatar_ids=["a"], pass_masks=["_img"], path=path)
        self.add_ons.extend([camera, capture])
        self.communicate(self.create_scene())
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = ProcGenRoom()
    c.run()
```

Result:

![](images/proc_gen_room_0.jpg)

## 3. Add a ceiling, adjust the walls, etc.

We can 


***

Python API:

- [`TDWUtils.get_box(width, length)`](../../python/tdw_utils.md)

Command API:

- [`load_scene`](../../api/command_api.md#load_scene)
- [`create_exterior_walls`](../../api/command_api.md#create_exterior_walls)
- [`create_interior_walls`](../../api/command_api.md#create_interior_walls)
- [`create_proc_gen_ceiling`](../../api/command_api.md#create_proc_gen_ceiling)
- [`set_proc_gen_ceiling_color`](../../api/command_api.md#set_proc_gen_ceiling_color)
- [`destroy_proc_gen_ceiling`](../../api/command_api.md#destroy_proc_gen_ceiling)
- [`create_proc_gen_ceiling_tiles`](../../api/command_api.md#create_proc_gen_ceiling_tiles)
- [`destroy_proc_gen_ceiling_tiles`](../../api/command_api.md#destroy_proc_gen_ceiling_tiles)