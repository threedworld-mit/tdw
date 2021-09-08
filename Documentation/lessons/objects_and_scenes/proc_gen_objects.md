##### Objects and Scenes

# Procedural generation  (objects)

This document will walk you through a simple example of how to use procedural generation to populate a scene with objects. [As noted at the start of this tutorial](overview.md), procedural generation is a powerful technique for quickly generating large numbers of scene environments. However, by its very nature, there is no single "canonical" algorithm for procedural generation. This document will describe *a* way to populate a scene with objects, not *the* way. It is also incomplete; the end of this document lists just some of the ways to improve the example code.

## 1. Choose a random table and a random chair

First, we're going to use numpy to create a RandomState with a seed. This is useful if you want to replicate the exact same procedurally generated scene:

```python
import numpy as np

rng = np.random.RandomState(seed=0)
```

Next, we need to get the `wnid` associated with `table` and with `chair`:

```python
from tdw.librarian import ModelLibrarian

librarian = ModelLibrarian()
wnids_and_categories = librarian.get_model_wnids_and_wcategories()
for wnid in wnids_and_categories:
    if wnids_and_categories[wnid] == "chair":
        print("chair", wnid) # chair n03001627
    elif wnids_and_categories[wnid] == "table":
        print("table", wnid) # table n04379243
```

Having done that, we can get a list of all tables and a list of all chairs. We'll then filter out any models flagged as `do_not_use`:

```python
from tdw.librarian import ModelLibrarian

librarian = ModelLibrarian()
tables = librarian.get_all_models_in_wnid("n04379243")
chairs = librarian.get_all_models_in_wnid("n03001627")
tables = [record for record in tables if not record.do_not_use]
chairs = [record for record in chairs if not record.do_not_use]
```

Then, we'll randomly select a chair model and a table model:

```python
import numpy as np
from tdw.librarian import ModelLibrarian

rng = np.random.RandomState(seed=0)
librarian = ModelLibrarian()
tables = librarian.get_all_models_in_wnid("n04379243")
chairs = librarian.get_all_models_in_wnid("n03001627")
tables = [record for record in tables if not record.do_not_use]
chairs = [record for record in chairs if not record.do_not_use]
table = tables[rng.randint(0, len(tables))]
chair = chairs[rng.randint(0, len(chairs))]
```

## 2. Create a scene

[As explained earlier in this tutorial](proc_gen_room.md), room generation can get quite complicated. We can also use a [streamed scene asset bundle](../core_concepts/scenes.md) which has less variability but looks better. Because this tutorial is about *object placement* rather than scene generation, we're just going to use the empty 12x12 room used in most tutorials:

```python
import numpy as np
from tdw.librarian import ModelLibrarian
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

rng = np.random.RandomState(seed=0)
librarian = ModelLibrarian()
tables = librarian.get_all_models_in_wnid("n04379243")
chairs = librarian.get_all_models_in_wnid("n03001627")
tables = [record for record in tables if not record.do_not_use]
chairs = [record for record in chairs if not record.do_not_use]
table = tables[rng.randint(0, len(tables))]
chair = chairs[rng.randint(0, len(chairs))]

c = Controller()
commands = [TDWUtils.create_empty_room(12, 12)]
```

## 3. Choose a position to add the table

We need to make sure that there is space for the table and its chairs. To do this, we'll used cached bounds data in the record to get the maximum extend of the table and chair:

```python
import numpy as np
from tdw.librarian import ModelLibrarian, ModelRecord
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

class ProcGen(Controller):
    @staticmethod
    def get_longest_extent(record: ModelRecord) -> float:
        left = TDWUtils.vector3_to_array(record.bounds["left"])
        right = TDWUtils.vector3_to_array(record.bounds["right"])
        front = TDWUtils.vector3_to_array(record.bounds["front"])
        back = TDWUtils.vector3_to_array(record.bounds["back"])
        left_right: float = np.linalg.norm(left - right)
        front_back: float = np.linalg.norm(front - back)
        if left_right > front_back:
            return left_right
        else:
            return front_back
    
    def run(self) -> None:
        rng = np.random.RandomState(seed=0)
        librarian = ModelLibrarian()
        tables = librarian.get_all_models_in_wnid("n04379243")
        chairs = librarian.get_all_models_in_wnid("n03001627")
        tables = [record for record in tables if not record.do_not_use]
        chairs = [record for record in chairs if not record.do_not_use]
        table = tables[rng.randint(0, len(tables))]
        chair = chairs[rng.randint(0, len(chairs))]
        
        table_extents = ProcGen.get_longest_extent(table)
        chair_extents = ProcGen.get_longest_extent(chair)
        
        commands = [TDWUtils.create_empty_room(12, 12)]
        
if __name__ == "__main__":
    c = ProcGen()
    c.run()
```

The table and chairs need to be placed in a free circle with a radius of `table_extents + chair_extents + n` where n is a little extra space. Using this radius and the known dimensions of the room, we can define a position for the table. Note that we're using `rng` in a few different functions now, so it's now defined as a field in the constructor. We'll also rotate the table for the sake of variability:

```python
import numpy as np
from tdw.librarian import ModelLibrarian, ModelRecord
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

class ProcGen(Controller):
    def __init__(self, port: int = 1071, launch_build: bool = True, random_seed: int = 0):
        super().__init__(port=port, launch_build=launch_build)
        self.rng: np.random.RandomState = np.random.RandomState(random_seed)

    @staticmethod
    def get_longest_extent(record: ModelRecord) -> float:
        left = TDWUtils.vector3_to_array(record.bounds["left"])
        right = TDWUtils.vector3_to_array(record.bounds["right"])
        front = TDWUtils.vector3_to_array(record.bounds["front"])
        back = TDWUtils.vector3_to_array(record.bounds["back"])
        left_right: float = np.linalg.norm(left - right)
        front_back: float = np.linalg.norm(front - back)
        if left_right > front_back:
            return left_right
        else:
            return front_back

    def get_table_placement_coordinate(self, radius: float) -> float:
        q = float(self.rng.uniform(0, 6 - radius))
        if self.rng.random() < 0.5:
            q *= -1
        return q

    def run(self) -> None:
        librarian = ModelLibrarian()
        tables = librarian.get_all_models_in_wnid("n04379243")
        chairs = librarian.get_all_models_in_wnid("n03001627")
        tables = [record for record in tables if not record.do_not_use]
        chairs = [record for record in chairs if not record.do_not_use]
        table = tables[self.rng.randint(0, len(tables))]
        chair = chairs[self.rng.randint(0, len(chairs))]

        table_extents = ProcGen.get_longest_extent(table)
        chair_extents = ProcGen.get_longest_extent(chair)
        table_placement_radius = table_extents + chair_extents + 1.15
        table_x = self.get_table_placement_coordinate(table_placement_radius)
        table_z = self.get_table_placement_coordinate(table_placement_radius)
        table_id = self.get_unique_id()

        commands = [TDWUtils.create_empty_room(12, 12),
                    self.get_add_object(model_name=table.name,
                                        position={"x": table_x, "y": 0, "z": table_z},
                                        rotation={"x": 0, "y": float(self.rng.uniform(-360, 360)), "z": 0},
                                        object_id=table_id)]

if __name__ == "__main__":
    c = ProcGen()
    c.run()
```

The easiest way to place chairs around a rotated table will be to used the table's rotated `Bounds` table. So, we'll request `Bounds` output data, and then send the commands we've listed so far:

```python
import numpy as np
from tdw.librarian import ModelLibrarian, ModelRecord
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import Bounds

class ProcGen(Controller):
    def __init__(self, port: int = 1071, launch_build: bool = True, random_seed: int = 0):
        super().__init__(port=port, launch_build=launch_build)
        self.rng: np.random.RandomState = np.random.RandomState(random_seed)

    @staticmethod
    def get_longest_extent(record: ModelRecord) -> float:
        left = TDWUtils.vector3_to_array(record.bounds["left"])
        right = TDWUtils.vector3_to_array(record.bounds["right"])
        front = TDWUtils.vector3_to_array(record.bounds["front"])
        back = TDWUtils.vector3_to_array(record.bounds["back"])
        left_right: float = np.linalg.norm(left - right)
        front_back: float = np.linalg.norm(front - back)
        if left_right > front_back:
            return left_right
        else:
            return front_back

    def get_table_placement_coordinate(self, radius: float) -> float:
        q = float(self.rng.uniform(0, 6 - radius))
        if self.rng.random() < 0.5:
            q *= -1
        return q

    def run(self) -> None:
        librarian = ModelLibrarian()
        tables = librarian.get_all_models_in_wnid("n04379243")
        chairs = librarian.get_all_models_in_wnid("n03001627")
        tables = [record for record in tables if not record.do_not_use]
        chairs = [record for record in chairs if not record.do_not_use]
        table = tables[self.rng.randint(0, len(tables))]
        chair = chairs[self.rng.randint(0, len(chairs))]

        table_extents = ProcGen.get_longest_extent(table)
        chair_extents = ProcGen.get_longest_extent(chair)
        table_placement_radius = table_extents + chair_extents + 1.15
        table_x = self.get_table_placement_coordinate(table_placement_radius)
        table_z = self.get_table_placement_coordinate(table_placement_radius)
        table_id = self.get_unique_id()

        resp = self.communicate([TDWUtils.create_empty_room(12, 12),
                                 self.get_add_object(model_name=table.name,
                                                     position={"x": table_x, "y": 0, "z": table_z},
                                                     rotation={"x": 0, "y": float(self.rng.uniform(-360, 360)), "z": 0},
                                                     object_id=table_id),
                                 {"$type": "send_bounds",
                                  "frequency": "once",
                                  "ids": [table_id]}])

if __name__ == "__main__":
    c = ProcGen()
    c.run()
```

## 3. Place chairs around the table

Parse `resp` to get the table's rotated bounds:

```python
import numpy as np
from tdw.librarian import ModelLibrarian, ModelRecord
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import Bounds

class ProcGen(Controller):
    def __init__(self, port: int = 1071, launch_build: bool = True, random_seed: int = 0):
        super().__init__(port=port, launch_build=launch_build)
        self.rng: np.random.RandomState = np.random.RandomState(random_seed)

    @staticmethod
    def get_longest_extent(record: ModelRecord) -> float:
        left = TDWUtils.vector3_to_array(record.bounds["left"])
        right = TDWUtils.vector3_to_array(record.bounds["right"])
        front = TDWUtils.vector3_to_array(record.bounds["front"])
        back = TDWUtils.vector3_to_array(record.bounds["back"])
        left_right: float = np.linalg.norm(left - right)
        front_back: float = np.linalg.norm(front - back)
        if left_right > front_back:
            return left_right
        else:
            return front_back

    def get_table_placement_coordinate(self, radius: float) -> float:
        q = float(self.rng.uniform(0, 6 - radius))
        if self.rng.random() < 0.5:
            q *= -1
        return q

    def run(self) -> None:
        librarian = ModelLibrarian()
        tables = librarian.get_all_models_in_wnid("n04379243")
        chairs = librarian.get_all_models_in_wnid("n03001627")
        tables = [record for record in tables if not record.do_not_use]
        chairs = [record for record in chairs if not record.do_not_use]
        table = tables[self.rng.randint(0, len(tables))]
        chair = chairs[self.rng.randint(0, len(chairs))]

        table_extents = ProcGen.get_longest_extent(table)
        chair_extents = ProcGen.get_longest_extent(chair)
        table_placement_radius = table_extents + chair_extents + 1.15
        table_x = self.get_table_placement_coordinate(table_placement_radius)
        table_z = self.get_table_placement_coordinate(table_placement_radius)
        table_id = self.get_unique_id()

        resp = self.communicate([TDWUtils.create_empty_room(12, 12),
                                 self.get_add_object(model_name=table.name,
                                                     position={"x": table_x, "y": 0, "z": table_z},
                                                     rotation={"x": 0, "y": float(self.rng.uniform(-360, 360)), "z": 0},
                                                     object_id=table_id),
                                 {"$type": "send_bounds",
                                  "frequency": "once",
                                  "ids": [table_id]}])
        # We know tha this is the only output data on this frame.
        bounds = Bounds(resp[0])
        # We know that the table is the only object in the output data.
        table_center = np.array(bounds.get_center(0))
        table_left = np.array(bounds.get_left(0))
        table_right = np.array(bounds.get_right(0))
        table_front = np.array(bounds.get_front(0))
        table_back = np.array(bounds.get_back(0))

if __name__ == "__main__":
    c = ProcGen()
    c.run()
```

We can use the bound positions of the table to get positions for the chairs. But we don't want to place the chairs *at* the bounds positions because then they'd intersect with the chair. Instead, they need to be offset from the bounds points. We'll define a vector from the center to the bounds point and offset each chair along that vector:

```python
import numpy as np
from tdw.librarian import ModelLibrarian, ModelRecord
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import Bounds

class ProcGen(Controller):
    def __init__(self, port: int = 1071, launch_build: bool = True, random_seed: int = 0):
        super().__init__(port=port, launch_build=launch_build)
        self.rng: np.random.RandomState = np.random.RandomState(random_seed)

    @staticmethod
    def get_longest_extent(record: ModelRecord) -> float:
        left = TDWUtils.vector3_to_array(record.bounds["left"])
        right = TDWUtils.vector3_to_array(record.bounds["right"])
        front = TDWUtils.vector3_to_array(record.bounds["front"])
        back = TDWUtils.vector3_to_array(record.bounds["back"])
        left_right: float = np.linalg.norm(left - right)
        front_back: float = np.linalg.norm(front - back)
        if left_right > front_back:
            return left_right
        else:
            return front_back

    def get_table_placement_coordinate(self, radius: float) -> float:
        q = float(self.rng.uniform(0, 6 - radius))
        if self.rng.random() < 0.5:
            q *= -1
        return q

    def get_chair_position(self, table_center: np.array, table_bound_point: np.array) -> np.array:
        position_to_center = table_bound_point - table_center
        position_to_center_normalized = position_to_center / np.linalg.norm(position_to_center)
        chair_position = table_bound_point + (position_to_center_normalized * self.rng.uniform(0.5, 0.125))
        chair_position[1] = 0
        return chair_position

    def run(self) -> None:
        librarian = ModelLibrarian()
        tables = librarian.get_all_models_in_wnid("n04379243")
        chairs = librarian.get_all_models_in_wnid("n03001627")
        tables = [record for record in tables if not record.do_not_use]
        chairs = [record for record in chairs if not record.do_not_use]
        table = tables[self.rng.randint(0, len(tables))]
        chair = chairs[self.rng.randint(0, len(chairs))]

        table_extents = ProcGen.get_longest_extent(table)
        chair_extents = ProcGen.get_longest_extent(chair)
        table_placement_radius = table_extents + chair_extents + 1.15
        table_x = self.get_table_placement_coordinate(table_placement_radius)
        table_z = self.get_table_placement_coordinate(table_placement_radius)
        table_id = self.get_unique_id()

        resp = self.communicate([TDWUtils.create_empty_room(12, 12),
                                 self.get_add_object(model_name=table.name,
                                                     position={"x": table_x, "y": 0, "z": table_z},
                                                     rotation={"x": 0, "y": float(self.rng.uniform(-360, 360)), "z": 0},
                                                     object_id=table_id),
                                 {"$type": "send_bounds",
                                  "frequency": "once",
                                  "ids": [table_id]}])
        # We know tha this is the only output data on this frame.
        bounds = Bounds(resp[0])
        # We know that the table is the only object in the output data.
        table_center = np.array(bounds.get_center(0))
        chair_positions = [self.get_chair_position(table_center=table_center, 
                                                   table_bound_point=np.array(bounds.get_left(0))),
                           self.get_chair_position(table_center=table_center,
                                                   table_bound_point=np.array(bounds.get_right(0))),
                           self.get_chair_position(table_center=table_center,
                                                   table_bound_point=np.array(bounds.get_front(0))),
                           self.get_chair_position(table_center=table_center,
                                                   table_bound_point=np.array(bounds.get_back(0)))]

if __name__ == "__main__":
    c = ProcGen()
    c.run()
```

To add each chair, we'll introduce two new commands. [`object_look_at_position`](../../api/command_api.md#object_look_at_position) rotates an object to point towards a position--in this case, the table's bottom-center position. [`rotate_object_by`](../../api/command_api.md#rotate_object_by) rotates an object by an angle an axis; we'll use this to rotate the chairs slightly for the sake of variability.

```python
import numpy as np
from tdw.librarian import ModelLibrarian, ModelRecord
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import Bounds

class ProcGen(Controller):
    def __init__(self, port: int = 1071, launch_build: bool = True, random_seed: int = 0):
        super().__init__(port=port, launch_build=launch_build)
        self.rng: np.random.RandomState = np.random.RandomState(random_seed)

    @staticmethod
    def get_longest_extent(record: ModelRecord) -> float:
        left = TDWUtils.vector3_to_array(record.bounds["left"])
        right = TDWUtils.vector3_to_array(record.bounds["right"])
        front = TDWUtils.vector3_to_array(record.bounds["front"])
        back = TDWUtils.vector3_to_array(record.bounds["back"])
        left_right: float = np.linalg.norm(left - right)
        front_back: float = np.linalg.norm(front - back)
        if left_right > front_back:
            return left_right
        else:
            return front_back

    def get_table_placement_coordinate(self, radius: float) -> float:
        q = float(self.rng.uniform(0, 6 - radius))
        if self.rng.random() < 0.5:
            q *= -1
        return q

    def get_chair_position(self, table_center: np.array, table_bound_point: np.array) -> np.array:
        position_to_center = table_bound_point - table_center
        position_to_center_normalized = position_to_center / np.linalg.norm(position_to_center)
        chair_position = table_bound_point + (position_to_center_normalized * self.rng.uniform(0.5, 0.125))
        chair_position[1] = 0
        return chair_position

    def run(self) -> None:
        librarian = ModelLibrarian()
        tables = librarian.get_all_models_in_wnid("n04379243")
        chairs = librarian.get_all_models_in_wnid("n03001627")
        tables = [record for record in tables if not record.do_not_use]
        chairs = [record for record in chairs if not record.do_not_use]
        table = tables[self.rng.randint(0, len(tables))]
        chair = chairs[self.rng.randint(0, len(chairs))]

        table_extents = ProcGen.get_longest_extent(table)
        chair_extents = ProcGen.get_longest_extent(chair)
        table_placement_radius = table_extents + chair_extents + 1.15
        table_x = self.get_table_placement_coordinate(table_placement_radius)
        table_z = self.get_table_placement_coordinate(table_placement_radius)
        table_id = self.get_unique_id()

        resp = self.communicate([TDWUtils.create_empty_room(12, 12),
                                 self.get_add_object(model_name=table.name,
                                                     position={"x": table_x, "y": 0, "z": table_z},
                                                     rotation={"x": 0, "y": float(self.rng.uniform(-360, 360)), "z": 0},
                                                     object_id=table_id),
                                 {"$type": "send_bounds",
                                  "frequency": "once",
                                  "ids": [table_id]}])
        # We know tha this is the only output data on this frame.
        bounds = Bounds(resp[0])
        # We know that the table is the only object in the output data.
        table_center = np.array(bounds.get_center(0))
        chair_positions = [self.get_chair_position(table_center=table_center,
                                                   table_bound_point=np.array(bounds.get_left(0))),
                           self.get_chair_position(table_center=table_center,
                                                   table_bound_point=np.array(bounds.get_right(0))),
                           self.get_chair_position(table_center=table_center,
                                                   table_bound_point=np.array(bounds.get_front(0))),
                           self.get_chair_position(table_center=table_center,
                                                   table_bound_point=np.array(bounds.get_back(0)))]
        table_bottom = TDWUtils.array_to_vector3(bounds.get_bottom(0))
        commands = []
        for chair_position in chair_positions:
            object_id = self.get_unique_id()
            commands.extend([self.get_add_object(model_name=chair.name,
                                                 position=TDWUtils.array_to_vector3(chair_position),
                                                 object_id=object_id),
                             {"$type": "object_look_at_position",
                              "position": table_bottom,
                              "id": object_id},
                             {"$type": "rotate_object_by",
                              "angle": float(self.rng.uniform(-20, 20)),
                              "id": object_id,
                              "axis": "yaw"}])
        self.communicate(commands)

if __name__ == "__main__":
    c = ProcGen()
    c.run()
```

## 4. Add a camera

Let's add a camera and enable image capture so we can view our handiwork. We'll take the top of the table's bounds and offset the camera from that point and point the camera at the table:

```python
import numpy as np
from tdw.librarian import ModelLibrarian, ModelRecord
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import Bounds
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

class ProcGen(Controller):
    def __init__(self, port: int = 1071, launch_build: bool = True, random_seed: int = 0):
        super().__init__(port=port, launch_build=launch_build)
        self.rng: np.random.RandomState = np.random.RandomState(random_seed)

    @staticmethod
    def get_longest_extent(record: ModelRecord) -> float:
        left = TDWUtils.vector3_to_array(record.bounds["left"])
        right = TDWUtils.vector3_to_array(record.bounds["right"])
        front = TDWUtils.vector3_to_array(record.bounds["front"])
        back = TDWUtils.vector3_to_array(record.bounds["back"])
        left_right: float = np.linalg.norm(left - right)
        front_back: float = np.linalg.norm(front - back)
        if left_right > front_back:
            return left_right
        else:
            return front_back

    def get_table_placement_coordinate(self, radius: float) -> float:
        q = float(self.rng.uniform(0, 6 - radius))
        if self.rng.random() < 0.5:
            q *= -1
        return q

    def get_chair_position(self, table_center: np.array, table_bound_point: np.array) -> np.array:
        position_to_center = table_bound_point - table_center
        position_to_center_normalized = position_to_center / np.linalg.norm(position_to_center)
        chair_position = table_bound_point + (position_to_center_normalized * self.rng.uniform(0.5, 0.125))
        chair_position[1] = 0
        return chair_position

    def run(self) -> None:
        librarian = ModelLibrarian()
        tables = librarian.get_all_models_in_wnid("n04379243")
        chairs = librarian.get_all_models_in_wnid("n03001627")
        tables = [record for record in tables if not record.do_not_use]
        chairs = [record for record in chairs if not record.do_not_use]
        table = tables[self.rng.randint(0, len(tables))]
        chair = chairs[self.rng.randint(0, len(chairs))]

        table_extents = ProcGen.get_longest_extent(table)
        chair_extents = ProcGen.get_longest_extent(chair)
        table_placement_radius = table_extents + chair_extents + 1.15
        table_x = self.get_table_placement_coordinate(table_placement_radius)
        table_z = self.get_table_placement_coordinate(table_placement_radius)
        table_id = self.get_unique_id()

        resp = self.communicate([TDWUtils.create_empty_room(12, 12),
                                 self.get_add_object(model_name=table.name,
                                                     position={"x": table_x, "y": 0, "z": table_z},
                                                     rotation={"x": 0, "y": float(self.rng.uniform(-360, 360)), "z": 0},
                                                     object_id=table_id),
                                 {"$type": "send_bounds",
                                  "frequency": "once",
                                  "ids": [table_id]}])
        # We know tha this is the only output data on this frame.
        bounds = Bounds(resp[0])
        # We know that the table is the only object in the output data.
        table_center = np.array(bounds.get_center(0))
        chair_positions = [self.get_chair_position(table_center=table_center,
                                                   table_bound_point=np.array(bounds.get_left(0))),
                           self.get_chair_position(table_center=table_center,
                                                   table_bound_point=np.array(bounds.get_right(0))),
                           self.get_chair_position(table_center=table_center,
                                                   table_bound_point=np.array(bounds.get_front(0))),
                           self.get_chair_position(table_center=table_center,
                                                   table_bound_point=np.array(bounds.get_back(0)))]
        table_top = bounds.get_top(0)
        camera = ThirdPersonCamera(position={"x": table_top[0] + 1.5, "y": table_top[1] + 0.7, "z": table_top[2] - 2},
                                   look_at=TDWUtils.array_to_vector3(table_top))
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("proc_gen_objects")
        print(f"Images will be saved to: {path}")
        capture = ImageCapture(avatar_ids=[camera.avatar_id], pass_masks=["_img"], path=path)
        self.add_ons.extend([camera, capture])
        table_bottom = TDWUtils.array_to_vector3(bounds.get_bottom(0))
        commands = []
        for chair_position in chair_positions:
            object_id = self.get_unique_id()
            commands.extend([self.get_add_object(model_name=chair.name,
                                                 position=TDWUtils.array_to_vector3(chair_position),
                                                 object_id=object_id),
                             {"$type": "object_look_at_position",
                              "position": table_bottom,
                              "id": object_id},
                             {"$type": "rotate_object_by",
                              "angle": float(self.rng.uniform(-20, 20)),
                              "id": object_id,
                              "axis": "yaw"}])
        self.communicate(commands)
        self.communicate({"$type": "terminate"})

if __name__ == "__main__":
    c = ProcGen()
    c.run()
```

Result:

![](images/proc_gen_objects.jpg)

## 5. Further improvements

As mentioned earlier, procedural generation is an unbounded problem and there's *always* room for improvement. You can expand upon this example in a number of ways:

- Refine the process of adding chairs so that they're slightly under the table top.
- Improve the placement of the table+chairs so that it works in a multi-room scene (such that the objects won't intersect with any interior walls).
- Add plates, cups, and so on to the top of the table.

***

**Next: [Reset a scene](reset_scene.md)**

[Return to the README](../../README.md)

***

Example controllers:

- [proc_gen_objects.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/objects_and_scenes/proc_gen_objects.py) Using procedural generation, add a table to scene and add chairs around the table.

Python API:

- [`ModelLibrarian.get_model_wnids_and_wcategories()`](../../python/librarian/model_librarian.md) Get a dictionary of WordNet IDs and categories.
- [`ModelLibrarian.get_all_models_in_wnid(wnid)`](../../python/librarian/model_librarian.md) Get all models with this WordNet ID.
- [`ModelRecord.do_not_use`](../../python/librarian/model_librarian.md) If True, don't use this model.
- [`ModelRecord.bounds`](../../python/librarian/model_librarian.md) Cached bounds of a model.
- [`TDWUtils.vector3_to_array`](../../python/tdw_utils.md) Concert an (x, y, z) dictionary to an [x, y, z] numpy array.

Command API:

- [`object_look_at_position`](../../api/command_api.md#object_look_at_position) 
- [`rotate_object_by`](../../api/command_api.md#rotate_object_by)

