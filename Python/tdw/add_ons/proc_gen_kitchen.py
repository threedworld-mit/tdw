from pathlib import Path
from pkg_resources import resource_filename
from json import loads
from typing import List, Dict, Optional, Tuple, Callable
import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.proc_gen_objects import ProcGenObjects
from tdw.cardinal_direction import CardinalDirection
from tdw.ordinal_direction import OrdinalDirection
from tdw.librarian import ModelRecord
from tdw.scene_data.region_walls import RegionWalls
from tdw.scene_data.room import Room
from tdw.add_ons.proc_gen_objects_data.lateral_sub_arrangement import LateralSubArrangement
from tdw.add_ons.proc_gen_kitchen_data.cabinetry import Cabinetry, CABINETRY


class ProcGenKitchen(ProcGenObjects):
    """
    Procedurally generate in a kitchen in a group of regions.
    """

    """:class_var
    Categories of models that can be placed on a shelf.
    """
    ON_SHELF: List[str] = Path(resource_filename(__name__, "proc_gen_kitchen_data/categories_on_shelf.txt")).read_text().split("\n")
    """:class_var
    Categories of models that can be placed in a basket.
    """
    IN_BASKET: List[str] = Path(resource_filename(__name__, "proc_gen_kitchen_data/categories_in_basket.txt")).read_text().split("\n")
    """:class_var
    Data for shelves. Key = model name. Value = Dictionary: "size" (a 2-element list), "ys" (list of shelf y's).
    """
    SHELF_DIMENSIONS: Dict[str, dict] = loads(Path(resource_filename(__name__, "proc_gen_kitchen_data/shelf_dimensions.json")).read_text())
    """:class_var
    The number of chairs around kitchen tables. Key = The number as a string. Value = A list of model names.
    """
    NUMBER_OF_CHAIRS_AROUND_TABLE: Dict[str, List[str]] = loads(Path(resource_filename(__name__, "proc_gen_kitchen_data/chairs_around_tables.json")).read_text())
    """:class_var
    Categories of "secondary objects".
    """
    SECONDARY_CATEGORIES: Dict[str, Dict[str, int]] = loads(Path(resource_filename(__name__, "proc_gen_kitchen_data/secondary_categories.json")).read_text())
    """:class_var
    The y value (height) of the wall cabinets.
    """
    WALL_CABINET_Y: float = 1.289581
    """:class_var
    A dictionary of the name of a kitchen counter model, and its corresponding wall cabinet.
    """
    COUNTERS_AND_CABINETS: Dict[str, str] = loads(Path(resource_filename(__name__, "proc_gen_kitchen_data/counters_and_cabinets.json")).read_text())
    """:class_var
    The rotations of the radiator models.
    """
    RADIATOR_ROTATIONS: dict = loads(Path(resource_filename(__name__, "proc_gen_kitchen_data/radiator_rotations.json")).read_text())
    """:class_var
    A dictionary of canonical rotations for kitchen objects. Key = The model name. Value = A dictionary: Key = The wall as a string. Value = The rotation in degrees.
    """
    OBJECT_ROTATIONS: Dict[str, Dict[str, int]] = loads(Path(resource_filename(__name__, "proc_gen_kitchen_data/object_rotations.json")).read_text())
    """:class_var
    Categories of models that are tall and might obscure windows.
    """
    TALL_CATEGORIES: List[str] = ["refrigerator", "shelf"]
    """:class_var
    Kitchen table models that can have centerpieces.
    """
    KITCHEN_TABLES_WITH_CENTERPIECES: List[str] = ["dining_room_table",
                                                   "enzo_industrial_loft_pine_metal_round_dining_table",
                                                   "b03_restoration_hardware_pedestal_salvaged_round_tables"]
    _DISHWASHER_OFFSET: float = 0.025

    def __init__(self, random_seed: int = None, print_random_seed: bool = True):
        """
        :param random_seed: The random seed. If None, a random seed is randomly selected.
        :param print_random_seed: If True, print the random seed. This can be useful for debugging.
        """

        super().__init__(random_seed=random_seed, print_random_seed=print_random_seed)
        self._cabinetry: Cabinetry = CABINETRY[0]

    def get_initialization_commands(self) -> List[dict]:
        """
        This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

        :return: A list of commands that will initialize this add-on.
        """

        commands = super().get_initialization_commands()
        # Add a dummy object.
        self.model_categories["kitchen_counter_top"] = ["kitchen_counter_top"]
        # Use only one radiator model per scene.
        self.model_categories["radiator"] = [self.model_categories["radiator"][self.rng.randint(0, len(self.model_categories["radiator"]))]]
        # Set the wood type and counter top visual material.
        self._cabinetry = CABINETRY[self.rng.randint(0, len(CABINETRY))]
        for category, model_names in zip(["kitchen_counter", "wall_cabinet", "sink"],
                                         self._cabinetry.counter_models, self._cabinetry.wall_cabinet_models,
                                         self._cabinetry.sink_models):
            self.model_categories[category] = [k for k in self.model_categories[category] if k in model_names]
        return commands

    def create(self, room: Room) -> None:
        """
        Create a kitchen. Populate it with a table and chairs, kitchen counters and wall cabinets, and appliances.
        Objects may be on top of or inside of larger objects.

        :param room: The [`Room`](../scene_data/room.md) that the kitchen is in.
        """

        alcoves = [alcove.walls for alcove in room.alcoves]
        region = room.main_region.walls
        # Set the true bounds.
        self.scene_bounds.rooms[room.main_region.bounds.region_id] = room.main_region.bounds
        for alcove in room.alcoves:
            self.scene_bounds.rooms[alcove.bounds.region_id] = alcove.bounds

        used_walls = self._add_initial_objects(region=region, alcoves=alcoves)
        self._add_secondary_arrangement(used_walls=used_walls, region=region,
                                        possible_categories=ProcGenKitchen.SECONDARY_CATEGORIES["main"])
        for alcove in alcoves:
            self._add_secondary_arrangement(used_walls=[], region=alcove,
                                            possible_categories=ProcGenKitchen.SECONDARY_CATEGORIES["alcove"])
        self.commands.append({"$type": "step_physics",
                              "frames": 50})

    def _add_initial_objects(self, region: RegionWalls, alcoves: List[RegionWalls]) -> List[CardinalDirection]:
        """
        Create the kitchen. Add kitchen appliances, counter tops, etc. and a table. Objects will be placed on surfaces.

        :param region: The [`RegionWalls`](../scene_data/region_walls.md) data describing the region.
        :param alcoves: A list of `RegionWalls` that are treated as part of a continuous kitchen, for example the smaller region of an L-shaped room.

        :return: The walls used by the work triangle.
        """

        # Add the work triangle.
        used_walls = self._add_work_triangle(region=region)
        # Add the table.
        self._add_table(region=region, used_walls=used_walls, alcoves=alcoves)
        return used_walls

    def _add_kitchen_counter(self, record: ModelRecord, position: Dict[str, float], wall: CardinalDirection,
                             direction: CardinalDirection, region: RegionWalls) -> None:
        """
        Procedurally generate a kitchen counter with objects on it.
        Sometimes, a kitchen counter will have a microwave, which can have objects on top of it.
        There will never be more than 1 microwave in the scene.

        :param record: The model record.
        :param position: The position of the root object.
        :param wall: The wall the kitchen counter is on.
        :param direction: The direction of the lateral arrangement.
        :param region: The `RegionWalls` data.

        :return: The model record of the root object. If no models were added to the scene, this is None.
        """

        rotation = ProcGenKitchen.OBJECT_ROTATIONS[record.name][wall.name]
        extents = TDWUtils.get_bounds_extents(bounds=record.bounds)
        kitchen_counter_position = self._get_position_along_wall(region=region.region_id,
                                                                 position=position,
                                                                 wall=wall,
                                                                 depth=extents[2],
                                                                 model_name=record.name)
        # Add objects on the kitchen counter.
        if extents[0] < 0.7 or "microwave" in self._used_unique_categories:
            self.add_object_with_other_objects_on_top(record=record,
                                                      position=kitchen_counter_position,
                                                      rotation=rotation,
                                                      category="kitchen_counter")
            # Add a wall cabinet if one exists and there is no window here.
            if record.name in ProcGenKitchen.COUNTERS_AND_CABINETS and region.walls_with_windows & wall == 0:
                wall_cabinet_model_name = ProcGenKitchen.COUNTERS_AND_CABINETS[record.name]
                wall_cabinet_record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(wall_cabinet_model_name)
                wall_cabinet_extents = TDWUtils.get_bounds_extents(bounds=wall_cabinet_record.bounds)
                room = self.scene_bounds.rooms[region.region_id]
                if wall == CardinalDirection.north:
                    wall_cabinet_position = {"x": kitchen_counter_position["x"],
                                             "y": ProcGenKitchen.WALL_CABINET_Y,
                                             "z": room.z_max - wall_cabinet_extents[2] / 2}
                elif wall == CardinalDirection.south:
                    wall_cabinet_position = {"x": kitchen_counter_position["x"],
                                             "y": ProcGenKitchen.WALL_CABINET_Y,
                                             "z": room.z_min + wall_cabinet_extents[2] / 2}
                elif wall == CardinalDirection.west:
                    wall_cabinet_position = {"x": room.x_min + wall_cabinet_extents[2] / 2,
                                             "y": ProcGenKitchen.WALL_CABINET_Y,
                                             "z": kitchen_counter_position["z"]}
                elif wall == CardinalDirection.east:
                    wall_cabinet_position = {"x": room.x_max - wall_cabinet_extents[2] / 2,
                                             "y": ProcGenKitchen.WALL_CABINET_Y,
                                             "z": kitchen_counter_position["z"]}
                else:
                    raise Exception(wall)
                self.commands.extend(Controller.get_add_physics_object(model_name=ProcGenKitchen.COUNTERS_AND_CABINETS[record.name],
                                                                       position=wall_cabinet_position,
                                                                       rotation={"x": 0, "y": rotation, "z": 0},
                                                                       object_id=Controller.get_unique_id(),
                                                                       library="models_core.json",
                                                                       kinematic=True))
        # Add a microwave on the kitchen counter.
        else:
            root_object_id = Controller.get_unique_id()
            self.commands.extend(Controller.get_add_physics_object(model_name=record.name,
                                                                   object_id=root_object_id,
                                                                   position=kitchen_counter_position,
                                                                   rotation={"x": 0, "y": rotation, "z": 0},
                                                                   library="models_core.json",
                                                                   kinematic=True))
            # Get the top position of the kitchen counter.
            object_top = {"x": kitchen_counter_position["x"],
                          "y": record.bounds["top"]["y"] + kitchen_counter_position["y"],
                          "z": kitchen_counter_position["z"]}
            microwave_model_names = self.model_categories["microwave"]
            microwave_model_name = microwave_model_names[self.rng.randint(0, len(microwave_model_names))]
            microwave_record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(microwave_model_name)
            # Add a microwave and add objects on top of the microwave.
            self.add_object_with_other_objects_on_top(record=microwave_record,
                                                      position=object_top,
                                                      rotation=rotation - 180,
                                                      category="microwave")
            self._used_unique_categories.append("microwave")

    def _add_refrigerator(self, record: ModelRecord, position: Dict[str, float], wall: CardinalDirection,
                          direction: CardinalDirection, region: RegionWalls) -> None:
        """
        Procedurally generate a refrigerator.

        :param record: The model record.
        :param position: The position of the root object.
        :param wall: The wall the kitchen counter is on.
        :param direction: The direction of the lateral arrangement.
        :param region: The `RegionWalls` data.

        :return: The model record of the root object. If no models were added to the scene, this is None.
        """

        rotation = ProcGenKitchen.OBJECT_ROTATIONS[record.name][wall.name]
        extents = TDWUtils.get_bounds_extents(bounds=record.bounds)
        self.commands.extend(Controller.get_add_physics_object(model_name=record.name,
                                                               object_id=Controller.get_unique_id(),
                                                               position=self._get_position_along_wall(region=region.region_id,
                                                                                                      position=position,
                                                                                                      wall=wall,
                                                                                                      depth=extents[2],
                                                                                                      model_name=record.name),
                                                               rotation={"x": 0, "y": rotation, "z": 0},
                                                               library="models_core.json",
                                                               kinematic=True))

    def _add_dishwasher(self, record: ModelRecord, position: Dict[str, float], wall: CardinalDirection,
                        direction: CardinalDirection, region: RegionWalls) -> None:
        """
        Procedurally generate a dishwasher.

        :param record: The model record.
        :param position: The position of the root object.
        :param wall: The wall the kitchen counter is on.
        :param direction: The direction of the lateral arrangement.
        :param region: The `RegionWalls` data.

        :return: The model record of the root object. If no models were added to the scene, this is None.
        """

        rotation = ProcGenKitchen.OBJECT_ROTATIONS[record.name][wall.name]
        # Shift the position a bit.
        if direction == CardinalDirection.north:
            position["z"] += ProcGenKitchen._DISHWASHER_OFFSET
        elif direction == CardinalDirection.south:
            position["z"] -= ProcGenKitchen._DISHWASHER_OFFSET
        elif direction == CardinalDirection.east:
            position["x"] += ProcGenKitchen._DISHWASHER_OFFSET
        elif direction == CardinalDirection.west:
            position["x"] -= ProcGenKitchen._DISHWASHER_OFFSET
        else:
            raise Exception(direction)
        extents = TDWUtils.get_bounds_extents(bounds=record.bounds)
        fridge_position = self._get_position_along_wall(region=region.region_id,
                                                        position=position,
                                                        wall=wall,
                                                        depth=extents[2],
                                                        model_name=record.name)
        # Add the dishwasher.
        self.commands.extend(Controller.get_add_physics_object(model_name=record.name,
                                                               object_id=Controller.get_unique_id(),
                                                               position=fridge_position,
                                                               rotation={"x": 0, "y": rotation, "z": 0},
                                                               library="models_core.json",
                                                               kinematic=True))
        # Shift the position a bit.
        if direction == CardinalDirection.north:
            position["z"] += ProcGenKitchen._DISHWASHER_OFFSET
        elif direction == CardinalDirection.south:
            position["z"] -= ProcGenKitchen._DISHWASHER_OFFSET
        elif direction == CardinalDirection.east:
            position["x"] += ProcGenKitchen._DISHWASHER_OFFSET
        elif direction == CardinalDirection.west:
            position["x"] -= ProcGenKitchen._DISHWASHER_OFFSET
        else:
            raise Exception(direction)
        # Add a kitchen counter top.
        size = (extents[0] + ProcGenKitchen._DISHWASHER_OFFSET * 2, self.cell_size)
        self._add_kitchen_counter_top_object(position={k: v for k, v in fridge_position.items()},
                                             wall=wall, size=size)

    def _add_stove(self, record: ModelRecord, position: Dict[str, float], wall: CardinalDirection,
                   direction: CardinalDirection, region: RegionWalls) -> None:
        """
        Procedurally generate a stove with objects on it.

        :param record: The model record.
        :param position: The position of the root object.
        :param wall: The wall the kitchen counter is on.
        :param direction: The direction of the lateral arrangement.
        :param region: The `RegionWalls` data.

        :return: The model record of the root object. If no models were added to the scene, this is None.
        """

        rotation = ProcGenKitchen.OBJECT_ROTATIONS[record.name][wall.name]
        extents = TDWUtils.get_bounds_extents(bounds=record.bounds)
        return self.add_object_with_other_objects_on_top(record=record,
                                                         position=self._get_position_along_wall(region=region.region_id,
                                                                                                position=position,
                                                                                                wall=wall,
                                                                                                depth=extents[2],
                                                                                                model_name=record.name),
                                                         rotation=rotation,
                                                         category="stove")
    
    def _add_kitchen_counter_top(self, record: ModelRecord, position: Dict[str, float], wall: CardinalDirection,
                                 direction: CardinalDirection, region: RegionWalls) -> None:
        """
        Add a floating (kinematic) kitchen counter top to the scene.

        :param record: The model record.
        :param position: The position of the root object.
        :param wall: The wall the kitchen counter is on.
        :param direction: The direction of the lateral arrangement.
        :param region: The `RegionWalls` data.

        :return: The model record of the root object. If no models were added to the scene, this is None.
        """
        
        self._add_kitchen_counter_top_object(position=position, wall=wall)

    def _add_kitchen_counter_top_object(self, position: Dict[str, float], wall: CardinalDirection,
                                        size: Tuple[float, float] = None) -> None:
        """
        Add a floating (kinematic) kitchen counter top to the scene.

        :param position: The position of the kitchen counter top. The y coordinate will be adjusted to be 0.9.
        :param wall: The wall.
        :param size: If not None, this is the (x, z) size of the counter top.
        """

        if size is None:
            scale_factor = {"x": self.cell_size, "y": 0.0371, "z": self.cell_size}
        else:
            scale_factor = {"x": size[0], "y": 0.0371, "z": size[1]}
        if wall == CardinalDirection.west or wall == CardinalDirection.east:
            rotation = 90
        else:
            rotation = 0
        object_id = Controller.get_unique_id()
        self.commands.extend([{"$type": "load_primitive_from_resources",
                               "primitive_type": "Cube",
                               "id": object_id,
                               "position": {"x": position["x"], "y": 0.9, "z": position["z"]},
                               "orientation": {"x": 0, "y": rotation, "z": 0}},
                              Controller.get_add_material(self._cabinetry.counter_top_material, "materials_med.json"),
                              {"$type": "set_primitive_visual_material",
                               "name": self._cabinetry.counter_top_material,
                               "id": object_id},
                              {"$type": "scale_object",
                               "id": object_id,
                               "scale_factor": scale_factor},
                              {"$type": "set_kinematic_state",
                               "id": object_id,
                               "is_kinematic": True}])
        # Add objects on top of the counter.
        self.add_rectangular_arrangement(size=(self.cell_size * 0.8, self.cell_size * 0.8),
                                         position={"x": position["x"], "y": 0.9167836, "z": position["z"]},
                                         categories=ProcGenObjects.ON_TOP_OF["kitchen_counter"])

    def _add_work_triangle(self, region: RegionWalls) -> List[CardinalDirection]:
        """
        Add a kitchen work triangle of counters and appliances.
        Source: https://kbcrate.com/kitchen-design-kitchen-work-triangle-improve-workspace/

        :param region: The [`RegionWalls`](../scene_data/region_walls.md) data describing the region.

        :return: A list of used walls.
        """

        longer_walls, length = self._get_longer_walls(region=region.region_id)
        longer_walls_ok = True
        for w in longer_walls:
            if region.non_continuous_walls & w == 0:
                longer_walls_ok = False
                break
        triangles: List[Callable[[RegionWalls], List[CardinalDirection]]] = [self._add_l_work_triangle]
        # Prefer parallel over straight.
        if longer_walls_ok:
            triangles.append(self._add_parallel_work_triangle)
        else:
            triangles.append(self._add_straight_work_triangle)
        shorter_walls, length = self._get_shorter_walls(region=region.region_id)
        shorter_walls_ok = True
        for w in shorter_walls:
            if region.non_continuous_walls & w == 0:
                shorter_walls_ok = False
                break
        if shorter_walls_ok:
            triangles.append(self._add_u_work_triangle)
        return self.rng.choice(triangles)(region=region)

    def _add_straight_work_triangle(self, region: RegionWalls) -> List[CardinalDirection]:
        """
        Add a lateral arrangement of kitchen counters and appliances along one of the longer walls.

        :param region: The [`RegionWalls`](../scene_data/region_walls.md) data describing the region.

        :return: A list of used walls.
        """

        longer_walls, length = self._get_longer_walls(region=region.region_id)
        ws = [w for w in longer_walls if region.non_continuous_walls & w == 0]
        # Prefer walls with windows, if possible.
        walls_with_windows = [w for w in ws if region.walls_with_windows & w != 0]
        if len(walls_with_windows) >= 1:
            longer_wall = walls_with_windows[self.rng.randint(0, len(walls_with_windows))]
        # Use either of the walls.
        else:
            longer_wall = self._get_wall(walls=longer_walls, non_continuous_walls=region.non_continuous_walls)
        corners = self._get_corners_from_wall(wall=longer_wall)
        corner = corners[self.rng.randint(0, len(corners))]
        position = self._get_corner_position(corner=corner, region=region.region_id)
        direction = self._get_direction_from_corner(corner=corner, wall=longer_wall)
        categories = ["refrigerator", "dishwasher", "sink", "kitchen_counter", "stove", "kitchen_counter", "shelf"]
        if self.rng.random() < 0.5:
            categories.reverse()
        categories = self._append_secondary_categories(categories=categories, wall=longer_wall, region=region)
        sub_arrangements = self._get_sub_arrangements(categories=categories, wall=longer_wall, region=region)
        self.add_lateral_arrangement(position=position, direction=direction, wall=longer_wall,
                                     sub_arrangements=sub_arrangements, length=length - self.cell_size / 2,
                                     region=region)
        return [longer_wall]

    def _add_parallel_work_triangle(self, region: RegionWalls) -> List[CardinalDirection]:
        """
        Add two lateral arrangements of kitchen counters and appliances along each of the longer walls.

        :param region: The [`RegionWalls`](../scene_data/region_walls.md) data describing the region.

        :return: A list of used walls.
        """

        lateral_0 = ["kitchen_counter", "stove", "kitchen_counter", "kitchen_counter", "kitchen_counter"]
        lateral_1 = ["refrigerator", "dishwasher", "sink", "kitchen_counter", "kitchen_counter"]
        longer_walls, length = self._get_longer_walls(region=region.region_id)
        # Prefer to place the sink at a wall with windows.
        ws = [w for w in longer_walls if region.non_continuous_walls & w == 0]
        walls_with_windows = [w for w in ws if region.walls_with_windows & w != 0]
        walls_without_windows = [w for w in ws if region.walls_with_windows & w == 0]
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
            categories = self._append_secondary_categories(categories=categories, wall=wall, region=region)
            corners = self._get_corners_from_wall(wall=wall)
            corner = corners[self.rng.randint(0, len(corners))]
            position = self._get_corner_position(corner=corner, region=region.region_id)
            direction = self._get_direction_from_corner(corner=corner, wall=wall)
            sub_arrangements = self._get_sub_arrangements(categories=categories, wall=wall, region=region)
            self.add_lateral_arrangement(position=position, direction=direction, wall=wall,
                                         sub_arrangements=sub_arrangements, length=length - self.cell_size / 2,
                                         region=region)
        return longer_walls

    def _add_l_work_triangle(self, region: RegionWalls) -> List[CardinalDirection]:
        """
        Add an L shape of two lateral arrangements of kitchen counters and appliances, one along one of the longer walls and one along one of the shorter walls.

        :param region: The [`RegionWalls`](../scene_data/region_walls.md) data describing the region.

        :return: A list of used walls.
        """

        longer_walls, length = self._get_longer_walls(region=region.region_id)
        # Prefer a wall with windows if possible.
        walls_with_windows = [w for w in longer_walls if region.walls_with_windows & w != 0]
        if len(walls_with_windows) >= 1:
            longer_wall = walls_with_windows[self.rng.randint(0, len(walls_with_windows))]
        # Use either of the walls.
        else:
            longer_wall = self._get_wall(walls=longer_walls, non_continuous_walls=region.non_continuous_walls)
        all_corners = self._get_corners_from_wall(wall=longer_wall)
        shorter_walls = []
        corners = []
        for corner in all_corners:
            shorter_wall = CardinalDirection(corner - longer_wall)
            if region.non_continuous_walls & shorter_wall == 0:
                shorter_walls.append(shorter_wall)
                corners.append(corner)
        corner = corners[self.rng.randint(0, len(corners))]
        position = self._get_corner_position(corner=corner, region=region.region_id)
        direction = self._get_direction_from_corner(corner=corner, wall=longer_wall)
        categories = ["floating_kitchen_counter_top", "sink", "dishwasher", "stove", "kitchen_counter", "shelf"]
        categories = self._append_secondary_categories(categories=categories, wall=longer_wall, region=region)
        sub_arrangements = self._get_sub_arrangements(categories=categories, wall=longer_wall, region=region)
        self.add_lateral_arrangement(position=position, direction=direction, wall=longer_wall,
                                     sub_arrangements=sub_arrangements, length=length - self.cell_size / 2,
                                     region=region)
        shorter_wall = CardinalDirection(corner - longer_wall)
        shorter_walls, length = self._get_shorter_walls(region=region.region_id)
        length -= self.cell_size
        # Get everything else.
        direction = self._get_direction_from_corner(corner=corner, wall=shorter_wall)
        position = self._get_corner_position(corner=corner, region=region.region_id)
        # Offset the position.
        position = self._get_position_offset_from_direction(position=position, direction=direction)
        category_lists = [["kitchen_counter", "kitchen_counter", "refrigerator", "shelf"],
                          ["kitchen_counter", "refrigerator", "kitchen_counter", "shelf"]]
        categories: List[str] = category_lists[self.rng.randint(0, len(category_lists))]
        sub_arrangements = self._get_sub_arrangements(categories=categories, wall=shorter_wall, region=region)
        self.add_lateral_arrangement(position=position, direction=direction, wall=shorter_wall,
                                     sub_arrangements=sub_arrangements, length=length, region=region)
        return [longer_wall, shorter_wall]

    def _add_u_work_triangle(self, region: RegionWalls) -> List[CardinalDirection]:
        """
        Add one long lateral arrangement and two shorter lateral arrangements in a U shape.

        :param region: The [`RegionWalls`](../scene_data/region_walls.md) data describing the region.

        :return: A list of used walls.
        """

        # Add the longer wall.
        longer_walls, length = self._get_longer_walls(region=region.region_id)
        # Prefer a wall with windows if possible.
        walls_with_windows = [w for w in longer_walls if region.walls_with_windows & w != 0]
        if len(walls_with_windows) >= 1:
            longer_wall = walls_with_windows[self.rng.randint(0, len(walls_with_windows))]
        # Use either of the walls.
        else:
            longer_wall = self._get_wall(walls=longer_walls, non_continuous_walls=region.non_continuous_walls)
        length -= self.cell_size
        corners = self._get_corners_from_wall(wall=longer_wall)
        corner = corners[self.rng.randint(0, len(corners))]
        position = self._get_corner_position(corner=corner, region=region.region_id)
        direction = self._get_direction_from_corner(corner=corner, wall=longer_wall)
        categories = ["sink", "kitchen_counter", "stove", "kitchen_counter"]
        categories = self._append_secondary_categories(categories=categories, wall=longer_wall, region=region)
        if self.rng.random() < 0.5:
            categories.reverse()
        categories.insert(0, "floating_kitchen_counter_top")
        # Fill the rest of the lateral arrangement.
        for i in range(20):
            categories.append("kitchen_counter")
        sub_arrangements = self._get_sub_arrangements(categories=categories, wall=longer_wall, region=region)
        self.add_lateral_arrangement(position=position, direction=direction, wall=longer_wall,
                                     sub_arrangements=sub_arrangements, length=length - self.cell_size / 2,
                                     region=region)
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
        opposite_corner_position = self._get_corner_position(corner=opposite_corner, region=region.region_id)
        # Add a counter top at the end.
        self._add_kitchen_counter_top_object(position=opposite_corner_position, wall=longer_wall)
        # Get the length of the shorter wall.
        shorter_walls, length = self._get_shorter_walls(region=region.region_id)
        length -= self.cell_size
        if self.rng.random() < 0.5:
            corners.reverse()
        for corner, categories in zip(corners, [["kitchen_counter", "refrigerator", "kitchen_counter", "shelf"],
                                                ["kitchen_counter", "dishwasher", "kitchen_counter", "kitchen_counter"]]):
            # Get the wall.
            shorter_wall = CardinalDirection(corner - longer_wall)
            # Get everything else.
            direction = self._get_direction_from_corner(corner=corner, wall=shorter_wall)
            position = self._get_corner_position(corner=corner, region=region.region_id)
            # Offset the position.
            position = self._get_position_offset_from_direction(position=position, direction=direction)
            sub_arrangements = self._get_sub_arrangements(categories=categories, wall=shorter_wall, region=region)
            self.add_lateral_arrangement(position=position, direction=direction, wall=shorter_wall,
                                         sub_arrangements=sub_arrangements, length=length, region=region)
        walls = [longer_wall]
        walls.extend(shorter_walls)
        return walls

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

    def _append_secondary_categories(self, categories: List[str], wall: CardinalDirection, region: RegionWalls) -> List[str]:
        """
        Append possible secondary categories to a list of main categories.

        :param categories: The list of main categories.
        :param wall: The wall.
        :param region: The region.

        :return: The extended list of categories.
        """

        possible_categories = []
        for c in ProcGenKitchen.SECONDARY_CATEGORIES["append"]:
            if c == "painting" and region.walls_with_windows & wall != 0:
                continue
            for i in range(ProcGenKitchen.SECONDARY_CATEGORIES["append"][c]):
                possible_categories.append(c)
        for i in range(10):
            categories.append(possible_categories[self.rng.randint(0, len(possible_categories))])
        return categories

    def _add_secondary_arrangement(self, used_walls: List[CardinalDirection], region: RegionWalls, possible_categories: Dict[str, int]) -> None:
        # Get a list of continuous unused walls.
        walls: List[CardinalDirection] = [c for c in CardinalDirection if region.non_continuous_walls & c == 0 and c not in used_walls]
        for wall in walls:
            wall_categories = []
            # Don't put paintings on windows.
            for c in possible_categories:
                if c == "painting" and region.walls_with_windows & wall != 0:
                    continue
                for i in range(possible_categories[c]):
                    wall_categories.append(c)
            categories = ["void"]
            for i in range(10):
                categories.append(wall_categories[self.rng.randint(0, len(wall_categories))])
            corners = self._get_corners_from_wall(wall=wall)
            corner = corners[self.rng.randint(0, len(corners))]
            position = self._get_corner_position(corner=corner, region=region.region_id)
            direction = self._get_direction_from_corner(corner=corner, wall=wall)
            position = self._get_position_offset_from_direction(position=position, direction=direction)
            direction = self._get_direction_from_corner(corner=corner, wall=wall)
            longer_walls, length = self._get_longer_walls(region=region.region_id)
            if wall not in longer_walls:
                shorter_walls, length = self._get_shorter_walls(region=region.region_id)
            length -= self.cell_size * 2
            sub_arrangements = self._get_sub_arrangements(categories=categories, wall=wall, region=region)
            self.add_lateral_arrangement(position=position, direction=direction, wall=wall,
                                         sub_arrangements=sub_arrangements, length=length, region=region,
                                         check_object_positions=True)

    def _add_radiator(self, record: ModelRecord, position: Dict[str, float], wall: CardinalDirection,
                      direction: CardinalDirection, region: RegionWalls) -> None:
        """
        Add a radiator to a wall.

        :param record: The model record.
        :param position: The position of the root object.
        :param wall: The wall the kitchen counter is on.
        :param direction: The direction of the lateral arrangement.
        :param region: The `RegionWalls` data.
        """

        rotation = ProcGenKitchen.RADIATOR_ROTATIONS[record.name]["rotations"][wall.name]
        extents = TDWUtils.get_bounds_extents(bounds=record.bounds)
        depth = extents[ProcGenKitchen.RADIATOR_ROTATIONS[record.name]["depth"]]
        self._used_unique_categories.append("radiator")
        self.commands.extend(Controller.get_add_physics_object(model_name=record.name,
                                                               object_id=Controller.get_unique_id(),
                                                               position=self._get_position_along_wall(region=region.region_id,
                                                                                                      position=position,
                                                                                                      wall=wall,
                                                                                                      depth=depth,
                                                                                                      model_name=record.name),
                                                               rotation={"x": 0, "y": rotation, "z": 0},
                                                               library="models_core.json",
                                                               kinematic=True))

    def _add_sink(self, record: ModelRecord, position: Dict[str, float], wall: CardinalDirection,
                  direction: CardinalDirection, region: RegionWalls) -> None:
        """
        Add a sink to the scene.

        :param record: The model record.
        :param position: The position of the root object.
        :param wall: The wall the kitchen counter is on.
        :param direction: The direction of the lateral arrangement.
        :param region: The `RegionWalls` data.
        """

        rotation = ProcGenKitchen.OBJECT_ROTATIONS[record.name][wall.name]
        extents = TDWUtils.get_bounds_extents(bounds=record.bounds)
        self.commands.extend(Controller.get_add_physics_object(model_name=record.name,
                                                               object_id=Controller.get_unique_id(),
                                                               position=self._get_position_along_wall(region=region.region_id,
                                                                                                      position=position,
                                                                                                      wall=wall,
                                                                                                      depth=extents[2],
                                                                                                      model_name=record.name),
                                                               rotation={"x": 0, "y": rotation, "z": 0},
                                                               library="models_core.json",
                                                               kinematic=True))

    def _get_sub_arrangements(self, region: RegionWalls, wall: CardinalDirection,
                              categories: List[str]) -> List[LateralSubArrangement]:
        """
        :param region: The region.
        :param wall: The wall of the lateral arrangement.
        :param categories: A list of categories.

        :return: A list of `LateralSubArrangement`.
        """

        sub_arrangements: List[LateralSubArrangement] = list()
        for category in categories:
            if region.walls_with_windows & wall != 0 and category in ProcGenKitchen.TALL_CATEGORIES:
                c = "kitchen_counter"
            else:
                c = category
            if c == "kitchen_counter":
                sub_arrangements.append(LateralSubArrangement(category=c, function=self._add_kitchen_counter))
            elif c == "dishwasher":
                sub_arrangements.append(LateralSubArrangement(category=c, function=self._add_dishwasher))
            elif c == "sink":
                sub_arrangements.append(LateralSubArrangement(category=c, function=self._add_sink))
            elif c == "stove":
                sub_arrangements.append(LateralSubArrangement(category=c, function=self._add_stove))
            elif c == "shelf":
                sub_arrangements.append(LateralSubArrangement(category=c, function=self._add_shelf))
            elif c == "side_table":
                sub_arrangements.append(LateralSubArrangement(category=c, function=self._add_side_table,
                                                              position_offset_multiplier=2))
            elif c == "radiator":
                if c in self._used_unique_categories:
                    sub_arrangements.append(LateralSubArrangement(category="basket", function=self._add_basket,
                                                                  position_offset_multiplier=2))
                else:
                    sub_arrangements.append(LateralSubArrangement(category=c, function=self._add_radiator,
                                                                  position_offset_multiplier=2))
            elif c == "suitcase":
                sub_arrangements.append(LateralSubArrangement(category=c, function=self._add_suitcase,
                                                              position_offset_multiplier=2))
            elif c == "painting":
                sub_arrangements.append(LateralSubArrangement(category=c, function=self._add_painting,
                                                              position_offset_multiplier=2))
            elif c == "basket":
                sub_arrangements.append(LateralSubArrangement(category=c, function=self._add_basket,
                                                              position_offset_multiplier=2))
            elif c == "stool":
                sub_arrangements.append(LateralSubArrangement(category=c, function=self._add_stool,
                                                              position_offset_multiplier=2))
            elif c == "kitchen_counter_top":
                sub_arrangements.append(LateralSubArrangement(category=c, function=self._add_kitchen_counter_top))
        return sub_arrangements
