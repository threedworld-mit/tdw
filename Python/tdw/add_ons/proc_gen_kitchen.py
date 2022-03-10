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
from tdw.proc_gen.arrangements.kitchen_cabinets.kitchen_cabinet_type import KitchenCabinetType
from tdw.proc_gen.arrangements.kitchen_cabinets.kitchen_cabinet_set import KitchenCabinetSet, CABINETRY
from tdw.proc_gen.arrangements.kitchen_table import KitchenTable


class ProcGenKitchen(AddOn):
    """
    TODO
    """
    """:class_var
    Categories of models that are tall and might obscure windows.
    """
    TALL_CATEGORIES: List[str] = ["refrigerator", "shelf"]
    """:class_var
    Categories of "secondary objects".
    """
    SECONDARY_CATEGORIES: Dict[str, Dict[str, int]] = loads(Path(resource_filename(__name__, "proc_gen_kitchen_data/secondary_categories.json")).read_text())

    def __init__(self, scene: Union[str, SceneRecord, Room, List[Union[str, SceneRecord]]], create_scene: bool = True, room_index: int = 0, rng: Union[int, np.random.RandomState] = None):
        """
        :param scene: The scene. Can be `str` (the name of the scene), [`SceneRecord`](../../python/librarian/scene_librarian.md), [`Room`](../scene_data/room.md), or `List[Union[str, SceneRecord]]` (a list of scene names or records, in which case a scene will be randomly selected). The scene must at least one room; see `SceneRecord.rooms`.
        :param create_scene: If True, create the scene as part of the scene setup (assuming that `scene` is `str` or `SceneRecord`).
        :param room_index: The index of the room in `SceneRecord.rooms`. If `scene` is type `Room`, this parameter is ignored.
        :param rng: Either a random seed, a random number generator, or None. If None, a new random number generator is created.
        """

        super().__init__()
        # Get the random number generator.
        if rng is None:
            """:field
            The random number generator
            """
            self.rng: np.random.RandomState = np.random.RandomState()
        elif isinstance(rng, int):
            self.rng = np.random.RandomState(rng)
        elif isinstance(rng, np.random.RandomState):
            self.rng = rng
        else:
            raise Exception(rng)
        self._scene_record: Optional[SceneRecord] = None
        self._create_scene: bool = create_scene
        """:field
        The kitchen [`Room`](../scene_data/room.md).
        """
        self.room: Room = self._get_room(scene=scene, room_index=room_index)
        # Set the cabinetry.
        cabinetry_type = [c for c in KitchenCabinetType]
        """:field
        The [`KitchenCabinetSet`](../proc_gen/kitchen_cabinets/kitchen_cabinet_set.md). This is set randomly.
        """
        self.cabinetry: KitchenCabinetSet = CABINETRY[cabinetry_type[self.rng.randint(0, len(cabinetry_type))]]
        self._allow_microwave: bool = True
        self._allow_radiator: bool = True

    def get_initialization_commands(self) -> List[dict]:
        if self._create_scene:
            commands = [Controller.get_add_scene(scene_name=self._scene_record.name)]
        else:
            commands = []
        # Get a work triangle.
        longer_walls, longer_length = self.room.main_region.get_longer_sides()
        both_longer_walls_ok = True
        for w in longer_walls:
            if self.room.main_region.non_continuous_walls & w == 0:
                both_longer_walls_ok = False
                break
        triangles: List[Callable[[], Tuple[List[dict], List[CardinalDirection]]]] = [self._add_l_work_triangle]
        # Prefer parallel over straight.
        if both_longer_walls_ok:
            triangles.append(self._add_parallel_work_triangle)
        else:
            triangles.append(self._add_straight_work_triangle)
        shorter_walls, shorter_length = self.room.main_region.get_shorter_sides()
        both_shorter_walls_ok = True
        for w in shorter_walls:
            if self.room.main_region.non_continuous_walls & w == 0:
                both_shorter_walls_ok = False
                break
        if both_shorter_walls_ok:
            triangles.append(self._add_u_work_triangle)
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
                                                                 possible_categories=ProcGenKitchen.SECONDARY_CATEGORIES["main"],
                                                                 tall_category_replacement="void"))
        # Add secondary arrangements in any alcoves.
        for alcove in self.room.alcoves:
            commands.extend(self._get_secondary_lateral_arrangements(used_walls=[],
                                                                     region=alcove,
                                                                     possible_categories=ProcGenKitchen.SECONDARY_CATEGORIES["alcove"],
                                                                     tall_category_replacement="basket"))
        # Allow objects to stop moving.
        commands.append({"$type": "step_physics",
                         "frames": 50})
        return commands

    def on_send(self, resp: List[bytes]) -> None:
        pass

    def reset(self, scene: Union[str, SceneRecord, Room, List[Union[str, SceneRecord]]], create_scene: bool = True, room_index: int = 0,
              rng: Union[int, np.random.RandomState] = None) -> None:
        """
        Reset the add-on. Call this when you reset a scene.

        :param scene: The scene. Can be `str` (the name of the scene), `SceneRecord`, `Room`, or `List[Union[str, SceneRecord]]` (a list of scene names or records, in which case a scene will be randomly selected). The scene must at least one room; see `SceneRecord.rooms`.
        :param create_scene: If True, create the scene as part of the scene setup (assuming that `scene` is `str` or `SceneRecord`).
        :param room_index: The index of the room in `SceneRecord.rooms`. If `scene` is type `Room`, this parameter is ignored.
        :param rng: Either a random seed, a random number generator, or None. If None, a new random number generator is created.
        """

        self.initialized = False
        self.commands.clear()
        if rng is None:
            self.rng = np.random.RandomState()
        elif isinstance(rng, int):
            self.rng = np.random.RandomState(rng)
        elif isinstance(rng, np.random.RandomState):
            self.rng = rng
        else:
            raise Exception(rng)
        # Set the room.
        self.room = self._get_room(scene=scene, room_index=room_index)
        # Set the cabinetry.
        cabinetry_type = [c for c in KitchenCabinetType]
        self.cabinetry = CABINETRY[cabinetry_type[self.rng.randint(0, len(cabinetry_type))]]
        # Allow appliances.
        self._allow_microwave = True
        self._allow_radiator = True

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
            self._scene_record = Controller.SCENE_LIBRARIANS["scenes.json"].get_record(scene)
            return self._scene_record.rooms[room_index]
        # This is a record.
        elif isinstance(scene, SceneRecord):
            self._scene_record = scene
            return self._scene_record.rooms[room_index]
        # This is a room. We can't create a scene if we didn't ask for one.
        elif isinstance(scene, Room):
            self._create_scene = False
            return scene
        # Choose a random scene.
        elif isinstance(scene, list):
            s = scene[self.rng.randint(0, len(scene))]
            if isinstance(s, str):
                self._scene_record = Controller.SCENE_LIBRARIANS["scenes.json"].get_record(s)
            elif isinstance(s, SceneRecord):
                self._scene_record = s
            else:
                raise Exception(s)
            return self._scene_record.rooms[room_index]
        else:
            raise Exception(self.room)

    def _get_lateral_arrangement(self, categories: List[str], corner: OrdinalDirection, wall: CardinalDirection,
                                 region: InteriorRegion, length: float = None, distance: float = 0) -> List[dict]:
        commands = []
        for category in categories:
            params = {"corner": corner,
                      "wall": wall,
                      "distance": distance,
                      "region": region,
                      "wall_length": length,
                      "rng": self.rng}
            if category == "basket":
                arrangement = Basket(**params)
            elif category == "dishwasher":
                p = {k: v for k, v in params.items()}
                p["cabinetry"] = self.cabinetry
                arrangement = Dishwasher(**p)
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
            if arrangement.send_commands:
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
        ws = [w for w in longer_walls if self.room.main_region.non_continuous_walls & w == 0]
        walls_with_windows = [w for w in ws if self.room.main_region.walls_with_windows & w != 0]
        walls_without_windows = [w for w in ws if self.room.main_region.walls_with_windows & w == 0]
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
                                            possible_categories: Dict[str, int], tall_category_replacement: str) -> List[dict]:
        """
        :param used_walls: A list of walls used in the primary arrangement (work triangle).
        :param region: The region.
        :param possible_categories: All possible categories for this arrangement.
        :param tall_category_replacement: If we need to replace tall objects, replace them with models from this category.

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
                                                          region=region))
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
            if region.walls_with_windows & wall != 0 and categories[i] in ProcGenKitchen.TALL_CATEGORIES:
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
        for c in ProcGenKitchen.SECONDARY_CATEGORIES["append"]:
            if c == "painting" and region.walls_with_windows & wall != 0:
                continue
            for i in range(ProcGenKitchen.SECONDARY_CATEGORIES["append"][c]):
                possible_categories.append(c)
        categories = [possible_categories[self.rng.randint(0, len(possible_categories))] for _ in range(10)]
        self._adjust_lateral_arrangement_categories(categories=categories,
                                                    wall=wall,
                                                    region=region,
                                                    tall_category_replacement="basket")
        return categories
