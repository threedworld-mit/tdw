from json import loads
from pathlib import Path
from pkg_resources import resource_filename
from typing import List, Dict, Union, Tuple, Callable, Optional
import numpy as np
from tdw.add_ons.add_on import AddOn
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import SceneLibrarian, SceneRecord
from tdw.cardinal_direction import CardinalDirection
from tdw.ordinal_direction import OrdinalDirection
from tdw.scene_data.room import Room
from tdw.scene_data.interior_region import InteriorRegion
from tdw.proc_gen.arrangements.arrangement import Arrangement
from tdw.proc_gen.arrangements.arrangement_along_wall import ArrangementAlongWall
from tdw.proc_gen.arrangements.basket import Basket
from tdw.proc_gen.arrangements.dishwasher import Dishwasher
from tdw.proc_gen.arrangements.kitchen_counter import KitchenCounter
from tdw.proc_gen.arrangements.painting import Painting
from tdw.proc_gen.arrangements.radiator import Radiator
from tdw.proc_gen.arrangements.refrigerator import Refrigerator
from tdw.proc_gen.arrangements.shelf import Shelf
from tdw.proc_gen.arrangements.side_table import SideTable
from tdw.proc_gen.arrangements.sink import Sink
from tdw.proc_gen.arrangements.stool import Stool
from tdw.proc_gen.arrangements.stove import Stove
from tdw.proc_gen.arrangements.suitcase import Suitcase
from tdw.proc_gen.arrangements.void import Void
from tdw.proc_gen.arrangements.kitchen_counter_top import KitchenCounterTop
from tdw.proc_gen.arrangements.cabinetry.cabinetry_type import CabinetryType
from tdw.proc_gen.arrangements.cabinetry.cabinetry import Cabinetry, CABINETRY
from tdw.proc_gen.arrangements.kitchen_table import KitchenTable


class ProcGenKitchen(AddOn):
    """
    Procedurally generate a kitchen in a new scene or an existing scene.

    ## Procedural generation algorithm

    This is an explanation of how `proc_gen_kitchen.create()` works.

    ### 1. Set the random number generator

    It is possible to explicitly set the random number generator via the `rng` parameter. Doing so will allow you to recreate the exact same scene later.

    ### 2. Set `self.room`

    If the `scene` parameter is of type [`Room`](../scene_data/room.md) this is straightforward. Otherwise, select a scene from the `scene` parameter (which will be loaded into TDW) and get the `Room` from the `room_index` parameter.

    ### 3. Select a set of cabinetry

    [`Cabinetry`](../proc_gen/arrangements/cabinetry/cabinetry.md) always visually match each other. A `Cabinetry` data object is selected randomly.

    ### 4. Create a work triangle

    A [work triangle](https://kbcrate.com/kitchen-design-kitchen-work-triangle-improve-workspace/) defines the overall design of the kitchen space.

    A work triangle is comprised of 1 or more _lateral arrangements_ of [`Arrangement`](../proc_gen/arrangements/arrangement.md) data objects along a wall, starting at a given distance from a corner.

    In all lateral arrangements in `ProcGenKitchen`, the following rules are always followed:

    - In the wall has windows, tall `Arrangements` will be replaced with shorter `Arrangements`; see `ProcGenKitchen.TALL_ARRANGEMENTS`. For work triangles, tall `Arrangements` will be replaced with [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md).
    - Non-continuous walls (e.g. a wall with a doorway) will never have a lateral arrangement.
    - Each wall has two corresponding corners. For example, a `north` wall has corners `north_west` and `north_east`. One of these corners is selected for the start of the lateral arrangement. Unless otherwise noted, the corner is chosen randomly.
    - A lateral arrangement has a list of `Arrangements`. They may not all fit along the wall, in which case as many `Arrangements` are added as possible.

    Work triangle lateral arrangements have the following additional shared rules:

    - Each work triangle lateral arrangement has *secondary arrangements* appended to its list to spatially lengthen it. Possibilities are: [[`Basket`](../proc_gen/arrangements/basket.md), [`Painting`](../proc_gen/arrangements/painting.md), [`Void`](../proc_gen/arrangements/void.md), [`Radiator`](../proc_gen/arrangements/radiator.md), [`Stool`](../proc_gen/arrangements/stool.md), [`Suitcase`](../proc_gen/arrangements/suitcase.md)]. The selection is random with weighted probability; see `ProcGenKitchen.SECONDARY_ARRANGEMENTS["append"]`.

    In TDW there are four possible work triangles:

    #### 4a. Straight

    A single lateral arrangement along one of the longer walls.

    **Requirements:** At least one continuous longer wall.

    1. If one of the longer walls has windows, it will be used for the lateral arrangement. Otherwise, the wall is chosen randomly.
    2. There are two possible lateral arrangements, chosen randomly:
      - [[`Refrigerator`](../proc_gen/arrangements/refrigerator.md), [`Dishwasher`](../proc_gen/arrangements/dishwasher.md), [`Sink`](../proc_gen/arrangements/sink.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Stove`](../proc_gen/arrangements/stove.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Shelf`](../proc_gen/arrangements/shelf.md)]
      - [[`Shelf`](../proc_gen/arrangements/shelf.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Stove`](../proc_gen/arrangements/stove.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Sink`](../proc_gen/arrangements/sink.md), [`Dishwasher`](../proc_gen/arrangements/dishwasher.md), [`Refrigerator`](../proc_gen/arrangements/refrigerator.md)]

    #### 4b. Parallel

    Two lateral arrangements along both longer walls.

    **Requirements:** Two continuous longer walls.

    1. If one of the longer walls has windows, it will be used for the lateral arrangement with the sink. Otherwise, each lateral arrangement uses a random longer wall.
    2. For the first lateral arrangement, there are two possibilities, chosen randomly:
      - [[`Refrigerator`](../proc_gen/arrangements/refrigerator.md), [`Dishwasher`](../proc_gen/arrangements/dishwasher.md), [`Sink`](../proc_gen/arrangements/sink.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md)]
      - [[`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Sink`](../proc_gen/arrangements/sink.md), [`Dishwasher`](../proc_gen/arrangements/dishwasher.md), [`Refrigerator`](../proc_gen/arrangements/refrigerator.md)]
    3. For the second lateral arrangement, there are two possibilities, chosen randomly:
      - [[`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Stove`](../proc_gen/arrangements/stove.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md)]
      - [[`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Stove`](../proc_gen/arrangements/stove.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md)]

    #### 4c. L-Shape

    One lateral arrangement along a longer wall and one lateral arrangement along a shorter wall. The two arrangements share a common corner.

    **Requirements:** At least one continuous longer wall and one continuous shorter wall.

    1. If one of the longer walls has windows, it will be used for the longer lateral arrangement. Otherwise, the wall is chosen randomly.
    2. There are two possible longer lateral arrangements, each with a `KitchenCounterTop` at the end. If both shorter walls are continuous, the selected lateral arrangement is random. Otherwise, `ProcGenKitchen` finds a corner shared by the longer wall and a continuous corner wall and selects the arrangement in which the `KitchenCounterTop` is placed at the common corner; for example if the longer wall is `north` and the only continuous wall is `west` then the longer arrangement is the first of the following two options because it `KitchenCounterTop` will be placed at the northwest corner.
      - [[`KitchenCounterTop`](../proc_gen/arrangements/kitchen_counter_top.md), [`Sink`](../proc_gen/arrangements/sink.md), [`Dishwasher`](../proc_gen/arrangements/dishwasher.md), [`Stove`](../proc_gen/arrangements/stove.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Shelf`](../proc_gen/arrangements/shelf.md)]
      - [[`Shelf`](../proc_gen/arrangements/shelf.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Stove`](../proc_gen/arrangements/stove.md), [`Dishwasher`](../proc_gen/arrangements/dishwasher.md), [`Sink`](../proc_gen/arrangements/sink.md), [`KitchenCounterTop`](../proc_gen/arrangements/kitchen_counter_top.md)]
    3. The shorter lateral arrangement is placed at the corresponding valid wall (see above). There are two possibilities, chosen randomly:
      - [[`Void`](../proc_gen/arrangements/void.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Refrigerator`](../proc_gen/arrangements/refrigerator.md), [`Shelf`](../proc_gen/arrangements/shelf.md)]
      - [[`Void`](../proc_gen/arrangements/void.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Refrigerator`](../proc_gen/arrangements/refrigerator.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Shelf`](../proc_gen/arrangements/shelf.md)]

    #### 4d. U-Shape

    One lateral arrangement along a longer wall and two lateral arrangements along both shorter walls.

    **Requirements:** At least one continuous longer wall and two continuous shorter walls.

    1. If one of the longer walls has windows, it will be used for the longer lateral arrangement. Otherwise, the wall is chosen randomly.
    2. There are two possible longer lateral arrangements, chosen randomly:
      - [[`KitchenCounterTop`](../proc_gen/arrangements/kitchen_counter_top.md), [`Sink`](../proc_gen/arrangements/sink.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Stove`](../proc_gen/arrangements/stove.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md)]
      - [[`KitchenCounterTop`](../proc_gen/arrangements/kitchen_counter_top.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Stove`](../proc_gen/arrangements/stove.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Sink`](../proc_gen/arrangements/sink.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md)]
    3. Each of the longer lateral arrangements will have additional 20 `KitchenCounters` appended. It is unlikely that there will ever actually be this many counters. Just before running out of space along the wall, the lateral arrangement will add a `KitchenCounterTop` instead (to anchor the corner).
    4. There are two possible shorter lateral arrangements. The wall on which they appear is chosen randomly:
      - [[`Void`](../proc_gen/arrangements/void.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Refrigerator`](../proc_gen/arrangements/refrigerator.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Shelf`](../proc_gen/arrangements/shelf.md)]
      - [[`Void`](../proc_gen/arrangements/void.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`Dishwasher`](../proc_gen/arrangements/dishwasher.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md), [`KitchenCounter`](../proc_gen/arrangements/kitchen_counter.md)]

    ***

    ### 5. Add a table

    Add a [`KitchenTable`](../proc_gen/arrangements/kitchen_table.md).

    The work triangles generate a list of commands and a list of used walls. This list of used walls is used as a parameter in `KitchenTable` to prevent chairs from intersecting with work triangle objects.

    ### 6. Add secondary arrangements

    Add secondary lateral arrangements to unused walls in the main region of the room and the walls of the alcove regions. See: `ProcGenKitchen.SECONDARY_ARRANGEMENTS["main"]` and  `ProcGenKitchen.SECONDARY_ARRANGEMENTS["alcove"]`.

    ### 7. Step 50 physics frames

    This allows objects to stop moving.

    ***

    """

    """:class_var
    [`Arrangements`](../proc_gen/arrangements/arrangement.md) that are tall and might obscure windows.
    """
    TALL_ARRANGEMENTS: List[str] = ["refrigerator", "shelf"]
    """:class_var
    A dictionary of "secondary arrangements". Keys: `"append"` (can be appended to a work triangle lateral arrangement), `"main"` (can be added to a lateral arrangement along an unused wall in the main [region](../scene_data/interior_region.md) of [`self.room`](../scene_data/room.md)), and `"alcove"` (can be added to a lateral arrangement along an unused wall of an alcove region). Value: A dictionary of probabilities and names of arrangements; a higher value means that it is more likely for this arrangement to be randomly selected.
    """
    SECONDARY_ARRANGEMENTS: Dict[str, Dict[str, int]] = loads(Path(resource_filename(__name__, "proc_gen_kitchen_data/secondary_categories.json")).read_text())
    """:class_var
    The names of the default scenes. If the `scene` parameter in `self.create()` isn't set, or is set to None, a random scene from this list will be selected.
    """
    SCENE_NAMES: List[str] = ['mm_craftroom_2a', 'mm_craftroom_2b', 'mm_craftroom_3a', 'mm_craftroom_3b', 'mm_kitchen_2a', 'mm_kitchen_2b', 'mm_kitchen_3a', 'mm_kitchen_3b']

    def __init__(self):
        """
        (no parameters)
        """

        super().__init__()
        """:field
        The random number generator.
        """
        self.rng: np.random.RandomState = np.random.RandomState()
        """:field
        The `SceneRecord` for this scene. This gets set by `self.create()` and can be None if the `scene` parameter is a [`Room`](../scene_data/room.md).
        """
        self.scene_record: Optional[SceneRecord] = None
        """:field
        The kitchen [`Room`](../scene_data/room.md). This gets set by `self.create()`.
        """
        self.room: Optional[Room] = None
        """:field
        The [`Cabinetry`](../proc_gen/arrangements/cabinetry/cabinetry.md). This is set randomly by `self.create()`.
        """
        self.cabinetry: Cabinetry = CABINETRY[CabinetryType.oak_white]
        self._allow_microwave: bool = True
        self._allow_radiator: bool = True
        self.initialized = True

    def create(self, scene: Union[str, SceneRecord, Room, List[Union[str, SceneRecord]]] = None, room_index: int = 0,
               cabinetry_type: CabinetryType = None, rng: Union[int, np.random.RandomState] = None) -> None:
        """
        Procedurally generate a kitchen. The kitchen will be created on the next `controller.communicate()` call.

        :param scene: Can be a string (the name of a scene), a [`SceneRecord`](../librarian/scene_librarian.md), a list of scene names and/or `SceneRecord` (one will chosen randomly), a [`Room`](../scene_data/room.md), or None. If this is a `Room`, then `ProcGenKitchen` will assume that the scene has already been loaded, and `self.scene_record` will be set to `None`. If `scene=None`, a random scene from `ProcGenKitchen.SCENE_NAMES` will be selected.
        :param room_index: The index of the room in `self.scene_record.rooms` (assuming `self.scene_record is not None`; see above).
        :param cabinetry_type: A [`CabinetryType`](../proc_gen/arrangements/cabinetry/cabinetry_type.md) value that sets which kitchen cabinets, wall cabinets, and sinks to add to the scene. If None, a `CabinetryType` is chosen randomly.
        :param rng: The random number generator. Can be `int` (a random seed), `np.random.RandomState`, or None (a new random seed will be selected randomly).
        """

        # Get the random number generator.
        if rng is None:
            self.rng = np.random.RandomState()
        elif isinstance(rng, int):
            self.rng = np.random.RandomState(rng)
        elif isinstance(rng, np.random.RandomState):
            self.rng = rng
        else:
            raise Exception(rng)
        create_scene = True
        # Create the librarian if it doesn't already exist.
        if "scenes.json" not in Controller.SCENE_LIBRARIANS:
            Controller.SCENE_LIBRARIANS["scenes.json"] = SceneLibrarian()
        # Get a random scene.
        if scene is None:
            scene = ProcGenKitchen.SCENE_NAMES[self.rng.randint(0, len(ProcGenKitchen.SCENE_NAMES))]
            self.scene_record = Controller.SCENE_LIBRARIANS["scenes.json"].get_record(scene)
            self.room = self.scene_record.rooms[room_index]
        # This is the name of a scene.
        if isinstance(scene, str):
            self.scene_record = Controller.SCENE_LIBRARIANS["scenes.json"].get_record(scene)
            self.room = self.scene_record.rooms[room_index]
        # This is a record.
        elif isinstance(scene, SceneRecord):
            self.scene_record = scene
            self.room = self.scene_record.rooms[room_index]
        # This is a room. We can't create a scene if we didn't ask for one.
        elif isinstance(scene, Room):
            self.room = scene
            self.scene_record = None
            create_scene = False
        # Choose a random scene.
        elif isinstance(scene, list):
            s = scene[self.rng.randint(0, len(scene))]
            if isinstance(s, str):
                self.scene_record = Controller.SCENE_LIBRARIANS["scenes.json"].get_record(s)
            elif isinstance(s, SceneRecord):
                self.scene_record = s
            else:
                raise Exception(s)
            self.room = self.scene_record.rooms[room_index]
        else:
            raise Exception(self.room)
        # Add the scene.
        if create_scene:
            commands = [Controller.get_add_scene(scene_name=self.scene_record.name)]
        # Use the existing scene.
        else:
            commands = []
        # Reset arrangement globals.
        self._allow_microwave = True
        self._allow_radiator = True
        # Set the cabinetry.
        if cabinetry_type is not None:
            self.cabinetry = CABINETRY[cabinetry_type]
        else:
            cabinetry_types = [c for c in CabinetryType]
            self.cabinetry = CABINETRY[cabinetry_types[self.rng.randint(0, len(cabinetry_types))]]
        # Get a work triangle.
        longer_walls, longer_length = self.room.main_region.get_longer_sides()
        both_longer_walls_ok = True
        continuous_longer_wall = False
        for w in longer_walls:
            if self.room.main_region.non_continuous_walls & w != 0:
                both_longer_walls_ok = False
            else:
                continuous_longer_wall = True
        shorter_walls, shorter_length = self.room.main_region.get_shorter_sides()
        both_shorter_walls_ok = True
        continuous_shorter_wall = False
        for w in shorter_walls:
            if self.room.main_region.non_continuous_walls & w != 0:
                both_shorter_walls_ok = False
            else:
                continuous_shorter_wall = True
        triangles: List[Callable[[], Tuple[List[dict], List[CardinalDirection]]]] = []
        if continuous_longer_wall:
            triangles.append(self._add_straight_work_triangle)
            if continuous_shorter_wall:
                triangles.append(self._add_l_work_triangle)
            if both_shorter_walls_ok:
                triangles.append(self._add_u_work_triangle)
            if both_longer_walls_ok:
                triangles.append(self._add_parallel_work_triangle)
        if len(triangles) == 0:
            return
        # Add the work triangle.
        triangle = triangles[self.rng.randint(0, len(triangles))]
        triangle_commands, used_walls = triangle()
        commands.extend(triangle_commands)
        # Add a kitchen table.
        kitchen_table = KitchenTable(room=self.room, used_walls=sum(used_walls), rng=self.rng)
        commands.extend(kitchen_table.get_commands())
        # Add secondary arrangements in the room.
        commands.extend(self._get_secondary_lateral_arrangements(used_walls=used_walls,
                                                                 region=self.room.main_region,
                                                                 possible_categories=ProcGenKitchen.SECONDARY_ARRANGEMENTS["main"],
                                                                 tall_category_replacement="void",
                                                                 current_commands=commands))
        # Add secondary arrangements in any alcoves.
        for alcove in self.room.alcoves:
            commands.extend(self._get_secondary_lateral_arrangements(used_walls=[],
                                                                     region=alcove,
                                                                     possible_categories=ProcGenKitchen.SECONDARY_ARRANGEMENTS["alcove"],
                                                                     tall_category_replacement="basket",
                                                                     current_commands=commands))
        # Allow objects to stop moving.
        commands.append({"$type": "step_physics",
                         "frames": 50})
        # Set the commands.
        self.commands = commands

    def get_initialization_commands(self) -> List[dict]:
        return []

    def on_send(self, resp: List[bytes]) -> None:
        pass

    def _get_room(self, scene: Union[str, SceneRecord, Room, List[Union[str, SceneRecord]]], room_index: int) -> Room:
        """
        :param scene: The scene. Can be `str` (the name of the scene), `SceneRecord`, `Room`, or `List[Union[str, SceneRecord]]` (a list of scene names or records, in which case a scene will be randomly selected). The scene must at least one room; see `SceneRecord.rooms`.
        :param room_index: The index of the room in `SceneRecord.rooms`. If `scene` is type `Room`, this parameter is ignored.

        :return: The `Room` in the scene.
        """

        # Create the librarian if it doesn't already exist.
        if "scenes.json" not in Controller.SCENE_LIBRARIANS:
            Controller.SCENE_LIBRARIANS["scenes.json"] = SceneLibrarian()
        # Get the record from the name.
        if isinstance(scene, str):
            self.scene_record = Controller.SCENE_LIBRARIANS["scenes.json"].get_record(scene)
            return self.scene_record.rooms[room_index]
        # This is a record.
        elif isinstance(scene, SceneRecord):
            self.scene_record = scene
            return self.scene_record.rooms[room_index]
        # This is a room. We can't create a scene if we didn't ask for one.
        elif isinstance(scene, Room):
            self._create_scene = False
            return scene
        # Choose a random scene.
        elif isinstance(scene, list):
            s = scene[self.rng.randint(0, len(scene))]
            if isinstance(s, str):
                self.scene_record = Controller.SCENE_LIBRARIANS["scenes.json"].get_record(s)
            elif isinstance(s, SceneRecord):
                self.scene_record = s
            else:
                raise Exception(s)
            return self.scene_record.rooms[room_index]
        else:
            raise Exception(self.room)

    def _get_lateral_arrangement(self, categories: List[str], corner: OrdinalDirection, wall: CardinalDirection,
                                 region: InteriorRegion, length: float = None, distance: float = 0,
                                 check_object_position: bool = False, current_commands: List[dict] = None) -> List[dict]:
        """
        Generate a lateral arrangement of Arrangements along a wall.

        :param categories: A sequential list of categories. This will be used to select Arrangement subclasses. This list might be adjusted, for example to remove categories of "tall" objects along a wall with windows.
        :param corner: The starting corner of the arrangement.
        :param wall: The wall that the arrangement will run along.
        :param region: The region that the arrangement is in.
        :param length: The length of the arrangement. If None, this is the length of the wall.
        :param distance: The starting distance from the corner.
        :param check_object_position: If True, check for objects added on this frame and avoid placing objects too close.
        :param current_commands: A list of commands added so far for this frame.

        :return: A list of commands to generate a lateral arrangement.
        """

        commands = []
        for category in categories:
            if check_object_position:
                occupied = False
                # Get the approximate position of the object.
                if wall == CardinalDirection.north:
                    z = region.z_max - Arrangement.DEFAULT_CELL_SIZE / 2
                    if corner == OrdinalDirection.northeast:
                        x = region.x_max
                    elif corner == OrdinalDirection.northwest:
                        x = region.x_min
                    else:
                        raise Exception(f"Invalid corner: {corner}")
                elif wall == CardinalDirection.south:
                    z = region.z_min + Arrangement.DEFAULT_CELL_SIZE / 2
                    if corner == OrdinalDirection.southeast:
                        x = region.x_max
                    elif corner == OrdinalDirection.southwest:
                        x = region.x_min
                    else:
                        raise Exception(f"Invalid corner: {corner}")
                elif wall == CardinalDirection.west:
                    x = region.x_min + Arrangement.DEFAULT_CELL_SIZE / 2
                    if corner == OrdinalDirection.northwest:
                        z = region.z_max
                    elif corner == OrdinalDirection.southwest:
                        z = region.z_min
                    else:
                        raise Exception(f"Invalid corner: {corner}")
                elif wall == CardinalDirection.east:
                    x = region.x_max - Arrangement.DEFAULT_CELL_SIZE / 2
                    if corner == OrdinalDirection.northeast:
                        z = region.z_max
                    elif corner == OrdinalDirection.southeast:
                        z = region.z_min
                    else:
                        raise Exception(f"Invalid corner: {corner}")
                else:
                    raise Exception(wall)
                direction = TDWUtils.get_direction_from_corner(corner=corner, wall=wall)
                if direction == CardinalDirection.north:
                    z += distance
                elif direction == CardinalDirection.south:
                    z -= distance
                elif direction == CardinalDirection.west:
                    x -= distance
                elif direction == CardinalDirection.east:
                    x += distance
                else:
                    raise Exception(direction)
                # Check if anything is nearby.
                p = np.array([x, z])
                if current_commands is not None:
                    for command in current_commands:
                        if command["$type"] != "add_object":
                            continue
                        if command["position"]["y"] > 0:
                            continue
                        else:
                            if "counter_top" in command["name"]:
                                model_library = "models_special.json"
                            else:
                                model_library = "models_core.json"
                            extents = TDWUtils.get_bounds_extents(bounds=Controller.MODEL_LIBRARIANS[model_library].get_record(command["name"]).bounds)
                            extent = (extents[0] if extents[0] > extents[2] else extents[2]) * 1.25
                        if np.linalg.norm(p - np.array([command["position"]["x"], command["position"]["z"]])) < extent:
                            occupied = True
                            break
                if occupied:
                    category = "void"
            params = {"corner": corner,
                      "wall": wall,
                      "distance": distance,
                      "region": region,
                      "wall_length": length,
                      "rng": self.rng}
            if category == "basket":
                arrangement = Basket(**params)
            elif category == "dishwasher":
                arrangement = Dishwasher(**params)
            elif category == "kitchen_counter":
                p = {k: v for k, v in params.items()}
                p["cabinetry"] = self.cabinetry
                p["allow_microwave"] = self._allow_microwave
                arrangement = KitchenCounter(**p)
            elif category == "floating_kitchen_counter_top":
                p = {k: v for k, v in params.items()}
                p["cabinetry"] = self.cabinetry
                arrangement = KitchenCounterTop(**p)
            elif category == "painting":
                arrangement = Painting(**params)
            elif category == "radiator":
                arrangement = Radiator(**params)
            elif category == "refrigerator":
                arrangement = Refrigerator(**params)
            elif category == "shelf":
                arrangement = Shelf(**params)
            elif category == "side_table":
                arrangement = SideTable(**params)
            elif category == "sink":
                p = {k: v for k, v in params.items()}
                p["cabinetry"] = self.cabinetry
                arrangement = Sink(**p)
            elif category == "stool":
                arrangement = Stool(**params)
            elif category == "stove":
                arrangement = Stove(**params)
            elif category == "suitcase":
                arrangement = Suitcase(**params)
            elif category == "void":
                arrangement = Void(corner=corner, wall=wall, distance=distance, region=region)
            else:
                raise Exception(category)
            # Add the commands.
            arrangement_commands = arrangement.get_commands()
            if (not isinstance(arrangement, ArrangementAlongWall)) or arrangement.send_commands:
                commands.extend(arrangement_commands)
                # Add the length.
                distance += arrangement.get_length()
                # Update the microwave state.
                if isinstance(arrangement, KitchenCounter) and arrangement.has_microwave:
                    self._allow_microwave = False
                # Update the radiator state.
                elif isinstance(arrangement, Radiator) and len(arrangement_commands) > 0:
                    self._allow_radiator = False
        return commands

    def _add_straight_work_triangle(self) -> Tuple[List[dict], List[CardinalDirection]]:
        """
        Add a lateral arrangement of kitchen counters and appliances along one of the longer walls.

        :return: Tuple: A list of commands, a list of used walls.
        """

        longer_walls, longer_length = self.room.main_region.get_longer_sides()
        ws = [w for w in longer_walls if self.room.main_region.non_continuous_walls & w == 0]
        # Prefer walls with windows, if possible.
        walls_with_windows = [w for w in ws if self.room.main_region.walls_with_windows & w != 0]
        if len(walls_with_windows) >= 1:
            longer_wall = walls_with_windows[self.rng.randint(0, len(walls_with_windows))]
        # Use either of the walls.
        else:
            longer_wall = self._get_wall(walls=longer_walls, non_continuous_walls=self.room.main_region.non_continuous_walls)
        all_corners = TDWUtils.get_corners_from_wall(wall=longer_wall)
        corner = all_corners[self.rng.randint(0, len(all_corners))]
        categories = ["refrigerator", "dishwasher", "sink", "kitchen_counter", "stove", "kitchen_counter", "shelf"]
        if self.rng.random() < 0.5:
            categories.reverse()
        categories.extend(self._get_secondary_categories(wall=longer_wall, region=self.room.main_region))
        self._adjust_lateral_arrangement_categories(categories=categories, wall=longer_wall, region=self.room.main_region)
        commands = self._get_lateral_arrangement(categories=categories,
                                                 corner=corner,
                                                 wall=longer_wall,
                                                 region=self.room.main_region,
                                                 length=longer_length - Arrangement.DEFAULT_CELL_SIZE / 2)
        return commands, [longer_wall]

    def _add_parallel_work_triangle(self) -> Tuple[List[dict], List[CardinalDirection]]:
        """
        Add two lateral arrangements of kitchen counters and appliances along each of the longer walls.

        :return: Tuple: A list of commands, a list of used walls.
        """

        lateral_0 = ["kitchen_counter", "stove", "kitchen_counter", "kitchen_counter", "kitchen_counter"]
        lateral_1 = ["refrigerator", "dishwasher", "sink", "kitchen_counter", "kitchen_counter"]
        longer_walls, longer_length = self.room.main_region.get_longer_sides()
        # Prefer to place the sink at a wall with windows.
        walls_with_windows = [w for w in longer_walls if self.room.main_region.walls_with_windows & w != 0]
        walls_without_windows = [w for w in longer_walls if self.room.main_region.walls_with_windows & w == 0]
        commands = []
        if len(walls_with_windows) >= 1:
            window_wall = walls_with_windows[self.rng.randint(0, len(walls_with_windows))]
            lateral_arrangements = [lateral_1, lateral_0]
            walls = [window_wall]
            walls.extend(walls_without_windows)
        # Use either of the walls.
        else:
            walls = longer_walls
            self.rng.shuffle(walls)
            lateral_arrangements = [lateral_0, lateral_1]
            self.rng.shuffle(lateral_arrangements)
        for wall, categories in zip(walls, lateral_arrangements):
            if self.rng.random() < 0.5:
                categories.reverse()
            categories.extend(self._get_secondary_categories(wall=wall, region=self.room.main_region))
            self._adjust_lateral_arrangement_categories(categories=categories, wall=wall, region=self.room.main_region)
            corners = TDWUtils.get_corners_from_wall(wall=wall)
            corner = corners[self.rng.randint(0, len(corners))]
            commands.extend(self._get_lateral_arrangement(categories=categories,
                                                          corner=corner,
                                                          wall=wall,
                                                          region=self.room.main_region))
        return commands, longer_walls

    def _add_l_work_triangle(self) -> Tuple[List[dict], List[CardinalDirection]]:
        """
        Add an L shape of two lateral arrangements of kitchen counters and appliances, one along one of the longer walls and one along one of the shorter walls.

        :return: Tuple: A list of commands, a list of used walls.
        """

        commands = []
        longer_walls, longer_length = self.room.main_region.get_longer_sides()
        # Prefer a wall with windows if possible.
        walls_with_windows = [w for w in longer_walls if self.room.main_region.walls_with_windows & w != 0]
        if len(walls_with_windows) >= 1:
            longer_wall = walls_with_windows[self.rng.randint(0, len(walls_with_windows))]
        # Use either of the walls.
        else:
            longer_wall = self._get_wall(walls=longer_walls, non_continuous_walls=self.room.main_region.non_continuous_walls)
        all_corners = TDWUtils.get_corners_from_wall(wall=longer_wall)
        shorter_walls = []
        corners = []
        for corner in all_corners:
            shorter_wall = CardinalDirection(corner - longer_wall)
            if self.room.main_region.non_continuous_walls & shorter_wall == 0:
                shorter_walls.append(shorter_wall)
                corners.append(corner)
        corner = corners[self.rng.randint(0, len(corners))]
        categories = ["floating_kitchen_counter_top", "sink", "dishwasher", "stove", "kitchen_counter", "shelf"]
        categories.extend(self._get_secondary_categories(wall=longer_wall, region=self.room.main_region))
        self._adjust_lateral_arrangement_categories(categories=categories,
                                                    wall=longer_wall,
                                                    region=self.room.main_region)
        commands.extend(self._get_lateral_arrangement(categories=categories,
                                                      corner=corner,
                                                      wall=longer_wall,
                                                      region=self.room.main_region))
        shorter_wall = CardinalDirection(corner - longer_wall)
        # Get everything else.
        category_lists = [["void", "kitchen_counter", "kitchen_counter", "refrigerator", "shelf"],
                          ["void", "kitchen_counter", "refrigerator", "kitchen_counter", "shelf"]]
        categories: List[str] = category_lists[self.rng.randint(0, len(category_lists))]
        self._adjust_lateral_arrangement_categories(categories=categories,
                                                    wall=shorter_wall,
                                                    region=self.room.main_region)
        # Set the distance to cell size to offset it from the floating kitchen counter top.
        commands.extend(self._get_lateral_arrangement(categories=categories,
                                                      corner=corner,
                                                      wall=shorter_wall,
                                                      region=self.room.main_region,
                                                      distance=Arrangement.DEFAULT_CELL_SIZE))
        return commands, [longer_wall, shorter_wall]

    def _add_u_work_triangle(self) -> Tuple[List[dict], List[CardinalDirection]]:
        """
        Add one long lateral arrangement and two shorter lateral arrangements in a U shape.

        :return: Tuple: A list of commands, a list of used walls.
        """

        commands = []
        # Add the longer wall.
        longer_walls, longer_length = self.room.main_region.get_longer_sides()
        # Prefer a wall with windows if possible.
        walls_with_windows = [w for w in longer_walls if self.room.main_region.walls_with_windows & w != 0]
        if len(walls_with_windows) >= 1:
            longer_wall = walls_with_windows[self.rng.randint(0, len(walls_with_windows))]
        # Use either of the walls.
        else:
            longer_wall = self._get_wall(walls=longer_walls,
                                         non_continuous_walls=self.room.main_region.non_continuous_walls)
        corners = TDWUtils.get_corners_from_wall(wall=longer_wall)
        corner = corners[self.rng.randint(0, len(corners))]
        categories = ["sink", "kitchen_counter", "stove", "kitchen_counter"]
        categories.extend(self._get_secondary_categories(wall=longer_wall, region=self.room.main_region))
        self._adjust_lateral_arrangement_categories(categories=categories, region=self.room.main_region, wall=longer_wall)
        if self.rng.random() < 0.5:
            categories.reverse()
        categories.insert(0, "floating_kitchen_counter_top")
        # Fill the rest of the lateral arrangement.
        for i in range(20):
            categories.append("kitchen_counter")
        commands.extend(self._get_lateral_arrangement(categories=categories,
                                                      corner=corner,
                                                      wall=longer_wall,
                                                      region=self.room.main_region,
                                                      length=longer_length - Arrangement.DEFAULT_CELL_SIZE))
        # Get the opposite corner.
        if longer_wall == CardinalDirection.north and corner == OrdinalDirection.northeast:
            opposite_corner = OrdinalDirection.northwest
        elif longer_wall == CardinalDirection.north and corner == OrdinalDirection.northwest:
            opposite_corner = OrdinalDirection.northeast
        elif longer_wall == CardinalDirection.south and corner == OrdinalDirection.southwest:
            opposite_corner = OrdinalDirection.southeast
        elif longer_wall == CardinalDirection.south and corner == OrdinalDirection.southeast:
            opposite_corner = OrdinalDirection.southwest
        elif longer_wall == CardinalDirection.west and corner == OrdinalDirection.northwest:
            opposite_corner = OrdinalDirection.southwest
        elif longer_wall == CardinalDirection.west and corner == OrdinalDirection.southwest:
            opposite_corner = OrdinalDirection.northwest
        elif longer_wall == CardinalDirection.east and corner == OrdinalDirection.northeast:
            opposite_corner = OrdinalDirection.southeast
        elif longer_wall == CardinalDirection.east and corner == OrdinalDirection.southeast:
            opposite_corner = OrdinalDirection.northeast
        else:
            raise Exception(longer_wall, corner)
        # Add a counter top at the end.
        commands.extend(self._get_lateral_arrangement(categories=["floating_kitchen_counter_top"],
                                                      corner=opposite_corner,
                                                      wall=longer_wall,
                                                      region=self.room.main_region))
        # Get the length of the shorter wall.
        shorter_walls, shorter_length = self.room.main_region.get_shorter_sides()
        if self.rng.random() < 0.5:
            corners.reverse()
        for corner, categories in zip(corners, [["void", "kitchen_counter", "refrigerator", "kitchen_counter", "shelf"],
                                                ["void", "kitchen_counter", "dishwasher", "kitchen_counter", "kitchen_counter"]]):
            # Get the wall.
            shorter_wall = CardinalDirection(corner - longer_wall)
            self._adjust_lateral_arrangement_categories(categories=categories,
                                                        region=self.room.main_region,
                                                        wall=shorter_wall)
            commands.extend(self._get_lateral_arrangement(categories=categories,
                                                          corner=corner,
                                                          wall=shorter_wall,
                                                          region=self.room.main_region,
                                                          length=shorter_length - Arrangement.DEFAULT_CELL_SIZE))
        walls = [longer_wall]
        walls.extend(shorter_walls)
        return commands, walls

    def _get_secondary_lateral_arrangements(self, used_walls: List[CardinalDirection], region: InteriorRegion,
                                            possible_categories: Dict[str, int], tall_category_replacement: str,
                                            current_commands: List[dict]) -> List[dict]:
        """
        :param used_walls: A list of walls used in the primary arrangement (work triangle).
        :param region: The region.
        :param possible_categories: All possible categories for this arrangement.
        :param tall_category_replacement: If we need to replace tall objects, replace them with models from this category.
        :param current_commands: The current list of commands. Used to check proximity.

        :return: A list of commands to add a secondary lateral arrangements on available walls.
        """

        random_categories = []
        for category in possible_categories:
            for i in range(possible_categories[category]):
                random_categories.append(category)
        # Add lateral arrangements to continuous unused walls.
        commands = []
        for wall in [c for c in CardinalDirection if (region.non_continuous_walls & c == 0) and c not in used_walls]:
            categories = []
            for i in range(10):
                categories.append(random_categories[self.rng.randint(0, len(random_categories))])
            self._adjust_lateral_arrangement_categories(categories=categories, region=region, wall=wall,
                                                        tall_category_replacement=tall_category_replacement)
            corners = TDWUtils.get_corners_from_wall(wall=wall)
            commands.extend(self._get_lateral_arrangement(categories=categories,
                                                          corner=corners[self.rng.randint(0, len(corners))],
                                                          wall=wall,
                                                          length=region.get_length(wall) - Arrangement.DEFAULT_CELL_SIZE,
                                                          distance=Arrangement.DEFAULT_CELL_SIZE * 2,
                                                          region=region,
                                                          check_object_position=True,
                                                          current_commands=current_commands))
        return commands

    def _adjust_lateral_arrangement_categories(self, categories: List[str], wall: CardinalDirection,
                                               region: InteriorRegion, tall_category_replacement: str = "kitchen_counter") -> None:
        """
        Adjust the lateral arrangement categories given the current scene state.

        - If the wall has windows, replace tall objects with shorter ones.
        - If there is already a radiator in the room, replace radiators with baskets.
        - Don't add paintings on a wall with windows.

        :param categories: The list of categories.
        :param wall: The wall.
        :param region: The region.
        :param tall_category_replacement: If we need to replace tall objects, replace them with models from this category.
        """

        for i in range(len(categories)):
            if region.walls_with_windows & wall != 0 and categories[i] in ProcGenKitchen.TALL_ARRANGEMENTS:
                categories[i] = tall_category_replacement
            elif region.walls_with_windows & wall != 0 and categories[i] == "painting":
                categories[i] = "void"
            elif categories[i] == "radiator" and not self._allow_radiator:
                categories[i] = "basket"

    def _get_wall(self, walls: List[CardinalDirection], non_continuous_walls: int) -> CardinalDirection:
        """
        :param walls: A list of walls.
        :param non_continuous_walls: Bitwise sum of non-continuous walls.

        :return: A valid continuous wall.
        """

        ws = [w for w in walls if non_continuous_walls & w == 0]
        if len(ws) == 0:
            raise Exception(non_continuous_walls, walls)
        if len(ws) == 1:
            return ws[0]
        else:
            return ws[self.rng.randint(0, len(ws))]

    def _get_secondary_categories(self, wall: CardinalDirection, region: InteriorRegion) -> List[str]:
        """
        :param wall: The wall.
        :param region: The region.

        :return: A list of secondary categories.
        """

        possible_categories = []
        for c in ProcGenKitchen.SECONDARY_ARRANGEMENTS["append"]:
            if c == "painting" and region.walls_with_windows & wall != 0:
                continue
            for i in range(ProcGenKitchen.SECONDARY_ARRANGEMENTS["append"][c]):
                possible_categories.append(c)
        categories = [possible_categories[self.rng.randint(0, len(possible_categories))] for _ in range(10)]
        self._adjust_lateral_arrangement_categories(categories=categories,
                                                    wall=wall,
                                                    region=region,
                                                    tall_category_replacement="basket")
        return categories
