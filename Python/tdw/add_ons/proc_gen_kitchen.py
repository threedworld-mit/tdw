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


class ProcGenKitchen(ProcGenObjects):
    """
    Procedurally generate in a kitchen in a group of regions.

    The kitchen always has 1 "main" rectangular region. It may have additional "alcoves", for example if the room is L-shaped.

    The kitchen will have a "work triangle" of kitchen counters and appliances, a kitchen table with chairs and table settings (forks, knives, etc.), and "secondary objects" such as paintings and baskets.

    ## Procedural generation rules

    ### 1. Non-continuous walls, walls with windows, and wall lengths

    Non-continuous walls are walls with gaps in the middle, such as doorways. Walls with windows have windows.

    - Objects will never be placed along non-continuous walls.
    - If a wall has windows, tall objects (see `ProcGenKitchen.TALL_CATEGORIES`) will be replaced with kitchen counters.
    - If a wall has windows, paintings will never be placed on it.

    For the sake of choosing walls for the "work triangles", `ProcGenKitchen` distinguishes between the two "longer walls" and the two "shorter walls" of the room.

    ### 2. Lateral arrangements and sub-arrangements

    `ProcGenKitchen` arranges kitchen countertops and appliances in plausible “work triangles” along the region’s walls. These stretches of adjacent objects are called "lateral arrangements" within this class's code.

    Each element in a lateral arrangement is a "sub-arrangement". A sub-arrangment maybe be a single object, but more often it is a group of objects, such as a kitchen counter with objects on top of it.

    ### 3. Work triangles

    Work triangles are comprised of lateral arrangements. In some cases, the list of categories may be reversible. These categories generate sub-arrangements.

    The following "work triangle" arrangements are possible:

    | Shape    | Requirements                                                 | Preference                                                   | Categories                                                   | Reversible      |
    | -------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | --------------- |
    | Straight | At least one continuous *longer* wall.                       | A wall with windows.                                      | `["refrigerator", "dishwasher", "sink", "kitchen_counter", "stove", "kitchen_counter", "shelf"]` | Yes             |
    | Parallel | Two continuous *longer* walls.                               | *Only for the list with the "sink":* A wall with windows. | `["kitchen_counter", "stove", "kitchen_counter", "kitchen_counter", "kitchen_counter"]`<br>`["refrigerator", "dishwasher", "sink", "kitchen_counter", "kitchen_counter"]` | Yes<br>Yes      |
    | L-Shape  | At least one continuous *longer* wall and one continuous *shorter* wall that share a corner. | *Longer wall:* A wall with windows.                       | *Longer wall:* `["floating_kitchen_counter_top", "sink", "dishwasher", "stove", "kitchen_counter", "shelf"]`<br><br>*Shorter wall:* `["kitchen_counter", "kitchen_counter", "refrigerator", "shelf"]` *OR* `["kitchen_counter", "refrigerator", "kitchen_counter", "shelf"]` | No<br>No        |
    | U-Shape  | At least one continuous *longer* wall. Two continuous *shorter* walls. | *Longer wall:* A wall with windows.                       | *Longer wall:* `["sink", "kitchen_counter", "stove", "kitchen_counter"]`<br>*Shorter wall:* `["kitchen_counter", "refrigerator", "kitchen_counter", "shelf"]` *OR* `["kitchen_counter", "dishwasher", "kitchen_counter", "kitchen_counter"]` | Yes<br>No<br>No |

    Additionally, the longer arrangement(s) of a "work triangle" may be extended with secondary sub-arrangements from the following categories: `["basket", "painting", "void", "radiator", "stool", "suitcase"]`.

    ### 4. Table arrangements

    The table model is chosen randomly.

    If there is at least one alcove that shares a non-continuous wall with the main region, then the table will be positioned near the shared boundary. If not, or if there are no alcoves, the table is placed in the center of the room, offset from the *used walls* of the "work triangle". For example, if the "work triangle" spans the north and west walls, then the table's position will be offset towards the southeast.

    The table's position and rotation are randomly perturbed.

    A table has 2-4 chairs around it depending on the model. The position and rotation of the chairs are randomly perturbed. The chairs are always the same model; the model is chosen randomly.

    Each chair has a corresponding "table setting" on the table. Table settings always include a plate (the position is perturbed randomly), a fork to the left of the plate, and a knife and spoon to the right of the plate. The models for the fork, spoon, and knife are randomly selected but are the same for each table setting. The positions and rotations of the fork, knife, and spoon are randomly perturbed. A table setting sometimes includes a cup in front of the plate and spoon (“front” in this case meaning “along a vector pointing to the center of the tabletop”). The cup can be either a mug or a wineglass. Sometimes, the cup is on a coaster. The cup and/or coaster’s rotation and position are perturbed randomly. Sometimes, there is food on the plate; the food is randomly selected. The food’s rotation and position are perturbed randomly.

    A table may have a random centerpiece object such as a jug or vase. The centerpiece position and rotation is perturbed randomly.

    ### 5. Secondary objects and arrangements

    Any unused continuous walls in each region (the main region as well as the alcoves) may have arrangements of *secondary objects* along each wall.

    The main region may have the following secondary sub-arrangements: side_table, basket, shelf, painting, void, radiator, stool, suitcase.

    Alcove regions may have the following secondary sub-arrangements: side_table, basket, painting, void, radiator, stool, suitcase.

    ### 6. Model sub-arrangements

    Unless otherwise noted, models will be rotated to face away from the wall they are adjacent to.

    #### Shelf

    A shelf model is chosen randomly from `ProcGenObjects.MODEL_CATEGORIES["shelf"]`.

    A shelving model has multiple “shelves”. Each shelf is a rectangular arrangement of objects from the following categories: book, bottle, bowl, candle, carving_fork, coaster, coffee_grinder, coffee_maker, coin, cork, cup, fork, house_plant, knife, ladle, jar, pan, pen, pot, scissors, soap_dispenser, spoon, tea_tray, vase

    #### Kitchen counter

    A kitchen counter model is chosen randomly from `ProcGenObjects.MODEL_CATEGORIES["kitchen_counter"]`.

    A kitchen counter can have objects on top of it from the following categories: apple, baking_sheet, banana, book, bottle, bowl, bread, candle, carving_fork, chocolate, coaster, coffee_grinder, coffee_maker, coin, cork, cup, fork, jar, jug, knife, ladle, orange, pan, pen, pepper, plate, pot, salt, sandwich, scissors, soap_dispenser, spaghetti_server, spatula, spoon, stove, tea_tray, teakettle, toaster, vase, whisk, wineglass

    A 36-inch kitchen counter may instead have a microwave on top of it. The microwave can have the following objects on top of it: apple, banana, bread, bowl, cup, house_plant, jar, jug, pen, scissors, tea_tray, vase.

    If the kitchen counter is on a wall that doesn’t have windows, it will also add a floating wall cabinet above it.

    When `ProcGenKitchen` is initialized, it uses one of two wood visual materials for the kitchen counters and wall cabinets and corresponding counter top visual materials.

    #### Floating kitchen counter top

    A floating kitchen countertop is a cube primitive scaled to look like a kitchen countertop. It is used for some vertical arrangements such as the Dishwasher and also in lateral arrangements at the corner of an L shape. These countertops can have objects on top of them from the same categories as with kitchen counters; they can’t have microwaves or kitchen cabinets.

    #### Refrigerator

    A refrigerator model is chosen randomly from `ProcGenObjects.MODEL_CATEGORIES["refrigerator"]`.

    #### Stove

    A stove model is chosen randomly from `ProcGenObjects.MODEL_CATEGORIES["stove"]`. A stove can have objects on top of it from the following categories: baking_sheet, pan, pot, teakettle. The models, positions, and rotations are random.

    #### Dishwasher

    A dishwasher model is chosen randomly from `ProcGenObjects.MODEL_CATEGORIES["dishwasher"]`.

    A dishwasher has a floating kitchen countertop on top of it, scaled to match the dishwasher’s dimensions. See above for how floating kitchen countertop arrangements work.

    #### Sink

    There are no sink models at present; a sink for now is a kitchen counter (see above).

    #### Basket

    A basket model is chosen randomly from `ProcGenObjects.MODEL_CATEGORIES["basket"]`.

    The basket object has a random rotation.

    A basket has objects within it. Objects are chosen from the following categories: coin, cork, fork, knife, pen, scissors, spoon. Baskets are at a random offset from the wall and have random rotations.

    Objects are initially placed above the basket at increasing heights. For example, if the first object is placed at y=0.25, the next object will be placed above it. This way, the objects won’t interpenetrate. These objects have random pitch, yaw, and roll rotations.

    #### Side table

    A side table model is chosen randomly from `ProcGenObjects.MODEL_CATEGORIES["side_table"]`.

    A side table can have objects on top of it from the following categories: book, bottle, bowl, candle, coffee_grinder, coffee_maker, house_plant, jar, jug.

    #### Painting

    A painting model is chosen randomly from `ProcGenObjects.MODEL_CATEGORIES["painting"]`.

    A painting is a kinematic framed painting “hanging” on the wall. Paintings have random y values between 1.1 and a maximum defined by (room_height - painting_height).

    #### Stool

    A stool model is chosen randomly from `ProcGenObjects.MODEL_CATEGORIES["stool"]`.

    Stools have random rotations.

    #### Stool

    A stool model is chosen randomly from `ProcGenObjects.MODEL_CATEGORIES["stool"]`.

    Stools have random rotations.

    #### Radiator

    A radiator model is chosen randomly from `ProcGenObjects.MODEL_CATEGORIES["radiator"]`.

    #### Suitcase

    A suitcase model is chosen randomly from `ProcGenObjects.MODEL_CATEGORIES["suitcase"]`.

    #### Void

    A void is a special null category that just creates a gap in the secondary lateral arrangement.
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
        self._counter_top_material: str = ""

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
        kitchen_counter_wood_type = self.rng.choice(["white_wood", "wood_beach_honey"])
        for category in ["kitchen_counter", "wall_cabinet", "sink"]:
            self.model_categories[category] = [k for k in self.model_categories[category] if kitchen_counter_wood_type in k]
        if kitchen_counter_wood_type == "white_wood":
            self._counter_top_material = "granite_beige_french"
        else:
            self._counter_top_material = "granite_black"
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

    def _add_table(self, region: RegionWalls, used_walls: List[CardinalDirection], alcoves: List[RegionWalls],
                   table_settings: bool = True, plate_model_name: str = None, fork_model_name: str = None,
                   knife_model_name: str = None, spoon_model_name: str = None,
                   centerpiece_model_name: str = None, offset_distance: float = 0.1) -> Optional[ModelRecord]:
        """
        Add a kitchen table with chairs around it.
        Optionally, add forks, knives, spoons, coasters, and cups.
        The plates sometimes have food on them.
        Sometimes, there is a large object (i.e. a bowl or jug) in the center of the table.

        :param region: The [`RegionWalls`](../scene_data/region_walls.md) data describing the region.
        :param used_walls: The walls used in the work triangle. This is used to offset the table position.
        :param alcoves: The alcoves in the room. If this is not None, the table might be halfway between the centers of the room.
        :param table_settings: If True, add tables settings (plates, forks, knives, etc.) in front of each chair.
        :param plate_model_name: If not None, this is the model name of the plates. If None, the plate is `plate06`.
        :param fork_model_name: If not None, this is the model name of the forks. If None, the model name of the forks is random (all fork objects use the same model).
        :param knife_model_name: If not None, this is the model name of the knives. If None, the model name of the knives is random (all knife objects use the same model).
        :param spoon_model_name: If not None, this is the model name of the spoons. If None, the model name of the spoons is random (all spoon objects use the same model).
        :param centerpiece_model_name: If not None, this is the model name of the centerpiece. If None, the model name of the centerpiece is random.
        :param offset_distance: Offset the position from the used walls by this distance.

        :return: The model record of the root object. If no models were added to the scene, this is None.
        """

        if plate_model_name is None:
            plate_model_name = "plate06"
        if fork_model_name is None:
            forks = self.model_categories["fork"]
            fork_model_name = forks[self.rng.randint(0, len(forks))]
        if knife_model_name is None:
            knives = self.model_categories["knife"]
            knife_model_name = knives[self.rng.randint(0, len(knives))]
        if spoon_model_name is None:
            spoons = self.model_categories["spoon"]
            spoon_model_name = spoons[self.rng.randint(0, len(spoons))]
        if centerpiece_model_name is None:
            centerpiece_categories = ["jug", "vase", "bowl"]
            centerpiece_category = centerpiece_categories[self.rng.randint(0, len(centerpiece_categories))]
            centerpieces = self.model_categories[centerpiece_category]
            centerpiece_model_name = centerpieces[self.rng.randint(0, len(centerpieces))]
        alcove: Optional[RegionWalls] = None
        # The main region and a valid alcove must share a non-continuous wall.
        if len(alcoves) > 0:
            for a in alcoves:
                for c in CardinalDirection:
                    try:
                        d = c << 2
                    except ValueError:
                        d = c >> 2
                    if region.non_continuous_walls & c != 0 and a.non_continuous_walls & d != 0:
                        alcove = a
                        break
        # If there are no valid alcoves, the position is in the center offset from the used walls.
        if alcove is None:
            room_center = self.scene_bounds.rooms[region.region].center
            position = {"x": room_center[0] + self.rng.uniform(-0.1, 0.1),
                        "y": 0,
                        "z": room_center[2] + self.rng.uniform(-0.1, 0.1)}
            # Apply offsets.
            if CardinalDirection.north in used_walls:
                position["z"] -= offset_distance
            if CardinalDirection.south in used_walls:
                position["z"] += offset_distance
            if CardinalDirection.east in used_walls:
                position["x"] -= offset_distance
            if CardinalDirection.west in used_walls:
                position["x"] += offset_distance
        # Position the table between the main region and an alcove.
        else:
            p = (np.array(self.scene_bounds.rooms[region.region].center) + np.array(self.scene_bounds.rooms[alcove.region].center)) * self.rng.uniform(0.35, 0.65)
            position = {"x": p[0] + self.rng.uniform(-0.1, 0.1),
                        "y": 0,
                        "z": p[2] + self.rng.uniform(-0.1, 0.1)}
        # Apply a random rotation.
        rotation = self.rng.uniform(-10, 10)
        # Add the table.
        root_object_id = Controller.get_unique_id()
        # Prefer a large table.
        if len(alcoves) > 0:
            tables = self.model_categories["large_kitchen_table"]
        else:
            tables = self.model_categories["kitchen_table"]
        table_model_name = tables[self.rng.randint(0, len(tables))]
        record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(table_model_name)
        self.commands.extend(Controller.get_add_physics_object(model_name=table_model_name,
                                                               position=position,
                                                               object_id=root_object_id,
                                                               library="models_core.json",
                                                               kinematic=True))
        child_object_ids: List[int] = list()
        # Get the shape of the table.
        table_shape = ""
        for shape in ProcGenKitchen.NUMBER_OF_CHAIRS_AROUND_TABLE:
            if record.name in ProcGenKitchen.NUMBER_OF_CHAIRS_AROUND_TABLE[shape]:
                table_shape = shape
                break
        assert table_shape != "", f"Unknown table shape for {record.name}"
        # Get the size, top, and bottom of the table.
        top = {"x": position["x"],
               "y": record.bounds["top"]["y"],
               "z": position["z"]}
        bottom = {"x": position["x"],
                  "y": 0,
                  "z": position["z"]}
        bottom_arr = TDWUtils.vector3_to_array(bottom)
        top_arr = TDWUtils.vector3_to_array(top)
        # Get a random chair model name.
        chairs = self.model_categories["chair"]
        chair_model_name: str = chairs[self.rng.randint(0, len(chairs))]
        chair_record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(chair_model_name)
        chair_bound_points: List[np.array] = list()
        # Add chairs around the table.
        if table_shape == "4":
            sides = ["left", "right", "front", "back"]
        # Add chairs on the shorter sides of the table.
        elif table_shape == "2":
            sides = ["front", "back"]
        else:
            raise Exception(table_shape)
        # Remove sides too close to used walls.
        tc = np.array([position["x"], position["z"]])
        for side_direction, cardinal_direction in zip(["front", "right", "back", "left"],
                                                      [c for c in CardinalDirection]):
            if side_direction in sides and cardinal_direction in used_walls:
                if cardinal_direction == CardinalDirection.north:
                    cp = np.array([position["x"], self.scene_bounds.rooms[region.region].z_max])
                elif cardinal_direction == CardinalDirection.south:
                    cp = np.array([position["x"], self.scene_bounds.rooms[region.region].z_min])
                elif cardinal_direction == CardinalDirection.west:
                    cp = np.array([self.scene_bounds.rooms[region.region].x_min, position["z"]])
                elif cardinal_direction == CardinalDirection.east:
                    cp = np.array([self.scene_bounds.rooms[region.region].x_max, position["z"]])
                else:
                    raise Exception(cardinal_direction)
                cd = np.linalg.norm(tc - cp)
                # Remove this side.
                if cd < 2:
                    sides.remove(side_direction)
        for side in sides:
            chair_bound_points.append(np.array([record.bounds[side]["x"] + position["x"],
                                                0,
                                                record.bounds[side]["z"] + position["z"]]))
        # Add the chairs.
        for chair_bound_point in chair_bound_points:
            chair_position = self._get_chair_position(chair_record=chair_record,
                                                      table_bottom=bottom_arr,
                                                      table_bound_point=chair_bound_point)
            object_id = Controller.get_unique_id()
            child_object_ids.append(object_id)
            # Add the chair.
            self.commands.extend(Controller.get_add_physics_object(model_name=chair_model_name,
                                                                   position=TDWUtils.array_to_vector3(chair_position),
                                                                   object_id=object_id,
                                                                   library="models_core.json"))
            # Look at the bottom-center and add a little rotation for spice.
            self.commands.extend([{"$type": "object_look_at_position",
                                   "position": bottom,
                                   "id": object_id},
                                  {"$type": "rotate_object_by",
                                   "angle": float(self.rng.uniform(-20, 20)),
                                   "id": object_id,
                                   "axis": "yaw"}])
        # Add table settings.
        if table_settings:
            for bound in sides:
                self._add_table_setting(position={"x": record.bounds[bound]["x"] + position["x"],
                                                  "y": 0,
                                                  "z": record.bounds[bound]["z"] + position["z"]},
                                        table_top=top,
                                        plate_model_name=plate_model_name,
                                        fork_model_name=fork_model_name,
                                        knife_model_name=knife_model_name,
                                        spoon_model_name=spoon_model_name)
        # Add a centerpiece.
        if self.rng.random() < 0.75 and table_model_name in ProcGenKitchen.KITCHEN_TABLES_WITH_CENTERPIECES:
            object_id = Controller.get_unique_id()
            child_object_ids.append(object_id)
            self.commands.extend(Controller.get_add_physics_object(model_name=centerpiece_model_name,
                                                                   object_id=object_id,
                                                                   position={"x": position["x"] + float(self.rng.uniform(-0.1, 0.1)),
                                                                             "y": float(top_arr[1]),
                                                                             "z": position["z"] + float(self.rng.uniform(-0.1, 0.1))},
                                                                   rotation={"x": 0,
                                                                             "y": float(self.rng.uniform(0, 360)),
                                                                             "z": 0},
                                                                   library="models_core.json"))
        self._add_rotation_commands(parent_object_id=root_object_id,
                                    child_object_ids=child_object_ids,
                                    rotation=rotation)
        return record

    def _add_shelf(self, record: ModelRecord, position: Dict[str, float], wall: CardinalDirection,
                   direction: CardinalDirection, region: RegionWalls) -> None:
        """
        Procedurally generate a shelf with objects on each shelf.

        :param record: The model record.
        :param position: The position of the root object.
        :param wall: The wall the kitchen counter is on.
        :param direction: The direction of the lateral arrangement.
        :param region: The `RegionWalls` data.

        :return: The model record of the root object. If no models were added to the scene, this is None.
        """

        # Add the shelf.
        root_object_id = Controller.get_unique_id()
        self.commands.extend(Controller.get_add_physics_object(model_name=record.name,
                                                               library="models_core.json",
                                                               object_id=root_object_id,
                                                               position={k: v for k, v in position.items()},
                                                               kinematic=True))
        size = (ProcGenKitchen.SHELF_DIMENSIONS[record.name]["size"][0], ProcGenKitchen.SHELF_DIMENSIONS[record.name]["size"][1])
        # Add objects to each shelf.
        child_object_ids: List[int] = list()
        for y in ProcGenKitchen.SHELF_DIMENSIONS[record.name]["ys"]:
            object_top = {"x": position["x"], "y": y + position["y"], "z": position["z"]}
            cell_size, density = self._get_rectangular_arrangement_parameters(category="shelf")
            object_ids = self.add_rectangular_arrangement(size=size,
                                                          categories=ProcGenKitchen.ON_SHELF,
                                                          position=object_top,
                                                          cell_size=cell_size,
                                                          density=density)
            child_object_ids.extend(object_ids)
        # Rotate everything.
        self._add_rotation_commands(parent_object_id=root_object_id,
                                    child_object_ids=child_object_ids,
                                    rotation=ProcGenKitchen.OBJECT_ROTATIONS[record.name][wall.name])

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
        kitchen_counter_position = self._get_position_along_wall(region=region.region,
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
                room = self.scene_bounds.rooms[region.region]
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
                                                               position=self._get_position_along_wall(region=region.region,
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
        fridge_position = self._get_position_along_wall(region=region.region,
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
                                                         position=self._get_position_along_wall(region=region.region,
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
                              Controller.get_add_material(self._counter_top_material, "materials_med.json"),
                              {"$type": "set_primitive_visual_material",
                               "name": self._counter_top_material,
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

    def _get_chair_position(self, chair_record: ModelRecord, table_bottom: np.array,
                            table_bound_point: np.array) -> np.array:
        """
        :param chair_record: The chair model record.
        :param table_bottom: The bottom-center position of the table.
        :param table_bound_point: The bounds position.

        :return: A position for a chair around the table.
        """

        position_to_center = table_bound_point - table_bottom
        position_to_center_normalized = position_to_center / np.linalg.norm(position_to_center)
        # Scoot the chair back by half of its front-back extent.
        half_extent = (np.linalg.norm(TDWUtils.vector3_to_array(chair_record.bounds["front"]) -
                                      TDWUtils.vector3_to_array(chair_record.bounds["back"]))) / 2
        # Move the chair position back. Add some randomness for spice.
        chair_position = table_bound_point + (position_to_center_normalized *
                                              (half_extent + self.rng.uniform(-0.1, -0.05)))
        chair_position[1] = 0
        return chair_position

    def _add_work_triangle(self, region: RegionWalls) -> List[CardinalDirection]:
        """
        Add a kitchen work triangle of counters and appliances.
        Source: https://kbcrate.com/kitchen-design-kitchen-work-triangle-improve-workspace/

        :param region: The [`RegionWalls`](../scene_data/region_walls.md) data describing the region.

        :return: A list of used walls.
        """

        longer_walls, length = self._get_longer_walls(region=region.region)
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
        shorter_walls, length = self._get_shorter_walls(region=region.region)
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

        longer_walls, length = self._get_longer_walls(region=region.region)
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
        position = self._get_corner_position(corner=corner, region=region.region)
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
        longer_walls, length = self._get_longer_walls(region=region.region)
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
            position = self._get_corner_position(corner=corner, region=region.region)
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

        longer_walls, length = self._get_longer_walls(region=region.region)
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
        position = self._get_corner_position(corner=corner, region=region.region)
        direction = self._get_direction_from_corner(corner=corner, wall=longer_wall)
        categories = ["floating_kitchen_counter_top", "sink", "dishwasher", "stove", "kitchen_counter", "shelf"]
        categories = self._append_secondary_categories(categories=categories, wall=longer_wall, region=region)
        sub_arrangements = self._get_sub_arrangements(categories=categories, wall=longer_wall, region=region)
        self.add_lateral_arrangement(position=position, direction=direction, wall=longer_wall,
                                     sub_arrangements=sub_arrangements, length=length - self.cell_size / 2,
                                     region=region)
        shorter_wall = CardinalDirection(corner - longer_wall)
        shorter_walls, length = self._get_shorter_walls(region=region.region)
        length -= self.cell_size
        # Get everything else.
        direction = self._get_direction_from_corner(corner=corner, wall=shorter_wall)
        position = self._get_corner_position(corner=corner, region=region.region)
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
        longer_walls, length = self._get_longer_walls(region=region.region)
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
        position = self._get_corner_position(corner=corner, region=region.region)
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
        opposite_corner_position = self._get_corner_position(corner=opposite_corner, region=region.region)
        # Add a counter top at the end.
        self._add_kitchen_counter_top_object(position=opposite_corner_position, wall=longer_wall)
        # Get the length of the shorter wall.
        shorter_walls, length = self._get_shorter_walls(region=region.region)
        length -= self.cell_size
        if self.rng.random() < 0.5:
            corners.reverse()
        for corner, categories in zip(corners, [["kitchen_counter", "refrigerator", "kitchen_counter", "shelf"],
                                                ["kitchen_counter", "dishwasher", "kitchen_counter", "kitchen_counter"]]):
            # Get the wall.
            shorter_wall = CardinalDirection(corner - longer_wall)
            # Get everything else.
            direction = self._get_direction_from_corner(corner=corner, wall=shorter_wall)
            position = self._get_corner_position(corner=corner, region=region.region)
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

    def _add_table_setting(self, position: Dict[str, float], table_top: Dict[str, float], plate_model_name: str,
                           fork_model_name: str, knife_model_name: str, spoon_model_name: str) -> None:
        """
        Add a table setting at a table.

        :param position: The bound point position. The plate position will be adjusted off of this.
        :param table_top: The position of the top-center of the table.
        :param plate_model_name: The model name of the plate.
        :param fork_model_name: The model name of the fork.
        :param knife_model_name: The model name of the knife.
        :param spoon_model_name: The model name of the spoon.
        """

        child_object_ids: List[int] = list()
        # Get the vector towards the center.
        v = np.array([position["x"], position["z"]]) - np.array([table_top["x"], table_top["z"]])
        # Get the normalized direction.
        v = v / np.linalg.norm(v)
        # Move the plates inward.
        v *= -float(self.rng.uniform(0.15, 0.2))
        # Get a slightly perturbed position for the plate.
        plate_position: Dict[str, float] = {"x": float(position["x"] + v[0] + self.rng.uniform(-0.03, 0.03)),
                                            "y": table_top["y"],
                                            "z": float(position["z"] + v[1] + self.rng.uniform(-0.03, 0.03))}
        # Add the plate.
        plate_id = Controller.get_unique_id()
        child_object_ids.append(plate_id)
        self.commands.extend(Controller.get_add_physics_object(model_name=plate_model_name,
                                                               position=plate_position,
                                                               object_id=plate_id,
                                                               library="models_core.json"))
        # Get the direction from the plate to the center.
        plate_record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(name=plate_model_name)
        plate_extents = TDWUtils.get_bounds_extents(bounds=plate_record.bounds)
        # Add a knife, fork, and spoon.
        fork_x = plate_position["x"] - (plate_extents[0] / 2 + self.rng.uniform(0.03, 0.05))
        knife_x = plate_position["x"] + plate_extents[0] / 2 + self.rng.uniform(0.03, 0.05)
        spoon_x = knife_x + self.rng.uniform(0.03, 0.07)
        for model_name, x in zip([fork_model_name, knife_model_name, spoon_model_name], [fork_x, knife_x, spoon_x]):
            object_id = Controller.get_unique_id()
            child_object_ids.append(object_id)
            self.commands.extend(Controller.get_add_physics_object(model_name=model_name,
                                                                   object_id=object_id,
                                                                   position={"x": x,
                                                                             "y": table_top["y"],
                                                                             "z": plate_position["z"] + self.rng.uniform(-0.03, 0.03)},
                                                                   rotation={"x": 0,
                                                                             "y": self.rng.uniform(-5, 5),
                                                                             "z": 0},
                                                                   library="models_core.json"))
        # Add a cup.
        if self.rng.random() > 0.33:
            cup_position = {"x": spoon_x + self.rng.uniform(-0.05, 0.01),
                            "y": table_top["y"],
                            "z": plate_position["z"] + plate_extents[2] / 2 + self.rng.uniform(0.06, 0.09)}
            # Add a coaster.
            if self.rng.random() > 0.5:
                coasters = self.model_categories["coaster"]
                coaster_model_name: str = coasters[self.rng.randint(0, len(coasters))]
                coaster_id = Controller.get_unique_id()
                child_object_ids.append(coaster_id)
                self.commands.extend(Controller.get_add_physics_object(model_name=coaster_model_name,
                                                                       position=cup_position,
                                                                       rotation={"x": 0,
                                                                                 "y": float(self.rng.randint(-25, 25)),
                                                                                 "z": 0},
                                                                       object_id=coaster_id,
                                                                       library="models_core.json"))
                coaster_record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(coaster_model_name)
                y = cup_position["y"] + coaster_record.bounds["top"]["y"]
            else:
                y = cup_position["y"]
            # Add a cup or wine glass.
            cups = self.model_categories["cup" if self.rng.random() < 0.5 else "wineglass"]
            cup_model_name = cups[self.rng.randint(0, len(cups))]
            # Add the cup.
            cup_id = Controller.get_unique_id()
            child_object_ids.append(cup_id)
            self.commands.extend(Controller.get_add_physics_object(model_name=cup_model_name,
                                                                   object_id=cup_id,
                                                                   position={"x": cup_position["x"],
                                                                             "y": y,
                                                                             "z": cup_position["z"]},
                                                                   rotation={"x": 0,
                                                                             "y": float(self.rng.uniform(0, 360)),
                                                                             "z": 0},
                                                                   library="models_core.json"))
        # Add food.
        if self.rng.random() < 0.66:
            food_categories = ["apple", "banana", "chocolate", "orange", "sandwich"]
            food_category: str = food_categories[self.rng.randint(0, len(food_categories))]
            food = self.model_categories[food_category]
            food_model_name = food[self.rng.randint(0, len(food))]
            food_id = Controller.get_unique_id()
            child_object_ids.append(food_id)
            self.commands.extend(Controller.get_add_physics_object(model_name=food_model_name,
                                                                   object_id=food_id,
                                                                   position={"x": plate_position["x"] + self.rng.uniform(-0.03, 0.03),
                                                                             "y": plate_position["y"] + plate_extents[1],
                                                                             "z": plate_position["z"] + self.rng.uniform(-0.03, 0.03)},
                                                                   rotation={"x": 0,
                                                                             "y": self.rng.uniform(0, 360),
                                                                             "z": 0},
                                                                   library="models_core.json"))
        # Parent everything to the plate.
        for child_object_id in child_object_ids:
            self.commands.append({"$type": "parent_object_to_object",
                                  "parent_id": plate_id,
                                  "id": child_object_id})
        # Rotate the plate to look at the center of the table.
        self.commands.append({"$type": "object_look_at_position",
                              "position": {"x": table_top["x"],
                                           "y": plate_position["y"],
                                           "z": table_top["z"]},
                              "id": plate_id})
        # Unparent everything.
        for child_object_id in child_object_ids:
            self.commands.append({"$type": "unparent_object",
                                  "id": child_object_id})

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
            position = self._get_corner_position(corner=corner, region=region.region)
            direction = self._get_direction_from_corner(corner=corner, wall=wall)
            position = self._get_position_offset_from_direction(position=position, direction=direction)
            direction = self._get_direction_from_corner(corner=corner, wall=wall)
            longer_walls, length = self._get_longer_walls(region=region.region)
            if wall not in longer_walls:
                shorter_walls, length = self._get_shorter_walls(region=region.region)
            length -= self.cell_size * 2
            sub_arrangements = self._get_sub_arrangements(categories=categories, wall=wall, region=region)
            self.add_lateral_arrangement(position=position, direction=direction, wall=wall,
                                         sub_arrangements=sub_arrangements, length=length, region=region,
                                         check_object_positions=True)

    def _add_side_table(self, record: ModelRecord, position: Dict[str, float], wall: CardinalDirection,
                        direction: CardinalDirection, region: RegionWalls) -> None:
        """
        Procedurally generate a side table with objects on it.

        :param record: The model record.
        :param position: The position of the root object.
        :param wall: The wall the kitchen counter is on.
        :param direction: The direction of the lateral arrangement.
        :param region: The `RegionWalls` data.
        """

        extents = TDWUtils.get_bounds_extents(bounds=record.bounds) * 1.05
        room = self.scene_bounds.rooms[region.region]
        if wall == CardinalDirection.north:
            side_table_position = {"x": position["x"],
                                   "y": 0,
                                   "z": room.z_max - extents[2]}
        elif wall == CardinalDirection.south:
            side_table_position = {"x": position["x"],
                                   "y": 0,
                                   "z": room.z_min + extents[2]}
        elif wall == CardinalDirection.west:
            side_table_position = {"x": room.x_min + extents[0],
                                   "y": 0,
                                   "z": position["z"]}
        elif wall == CardinalDirection.east:
            side_table_position = {"x": room.x_max - extents[0],
                                   "y": 0,
                                   "z": position["z"]}
        else:
            raise Exception(wall)
        rotation = ProcGenKitchen.OBJECT_ROTATIONS[record.name][wall.name]
        return self.add_object_with_other_objects_on_top(record=record,
                                                         position=side_table_position,
                                                         rotation=rotation,
                                                         category="side_table")

    def _add_basket(self, record: ModelRecord, position: Dict[str, float], wall: CardinalDirection,
                    direction: CardinalDirection, region: RegionWalls) -> None:
        """
        Procedurally generate a basket with objects in it.

        :param record: The model record.
        :param position: The position of the root object.
        :param wall: The wall the kitchen counter is on.
        :param direction: The direction of the lateral arrangement.
        :param region: The `RegionWalls` data.
        """

        rotation = self.rng.uniform(-10, 10)
        extents = TDWUtils.get_bounds_extents(bounds=record.bounds)
        basket_position = self._get_position_along_wall(model_name=record.name,
                                                        position=position,
                                                        wall=wall,
                                                        region=region.region,
                                                        depth=extents[2] * self.rng.uniform(1.15, 1.25))
        width = ProcGenKitchen.BOUNDS_OFFSETS[record.name]["width"] / 2
        if direction == CardinalDirection.north:
            basket_position["z"] += width
        elif direction == CardinalDirection.south:
            basket_position["z"] -= width
        elif direction == CardinalDirection.west:
            basket_position["x"] -= width
        else:
            basket_position["x"] += width
        self.commands.extend(Controller.get_add_physics_object(model_name=record.name,
                                                               object_id=Controller.get_unique_id(),
                                                               position=basket_position,
                                                               rotation={"x": 0, "y": rotation, "z": 0},
                                                               library="models_core.json",
                                                               kinematic=False))
        extents = TDWUtils.get_bounds_extents(bounds=record.bounds)
        d = extents[0] if extents[0] < extents[2] else extents[2]
        d *= 0.6
        r = d / 2
        y = extents[1]
        for i in range(2, self.rng.randint(4, 6)):
            category = ProcGenKitchen.IN_BASKET[self.rng.randint(0, len(ProcGenKitchen.IN_BASKET))]
            model_names = self.model_categories[category]
            model_name = model_names[self.rng.randint(0, len(model_names))]
            q = TDWUtils.get_random_point_in_circle(center=np.array([basket_position["x"], y, basket_position["z"]]),
                                                    radius=r)
            q[1] = y
            self.commands.extend(Controller.get_add_physics_object(model_name=model_name,
                                                                   object_id=Controller.get_unique_id(),
                                                                   position=TDWUtils.array_to_vector3(q),
                                                                   rotation={"x": float(self.rng.uniform(0, 360)),
                                                                             "y": float(self.rng.uniform(0, 360)),
                                                                             "z": float(self.rng.uniform(0, 360))},
                                                                   library="models_core.json"))
            y += 0.25

    def _add_painting(self, record: ModelRecord, position: Dict[str, float], wall: CardinalDirection,
                      direction: CardinalDirection, region: RegionWalls) -> None:
        """
        Add a painting to a wall.

        :param record: The model record.
        :param position: The position of the root object.
        :param wall: The wall the kitchen counter is on.
        :param direction: The direction of the lateral arrangement.
        :param region: The `RegionWalls` data.
        """

        # Rotate the painting and move it flush to the wall.
        extents = TDWUtils.get_bounds_extents(bounds=record.bounds)
        depth = extents[2]
        painting_position = {k: v for k, v in position.items()}
        if wall == CardinalDirection.north:
            painting_position["z"] = self.scene_bounds.rooms[region.region].z_max - depth
            rotation = 180
        elif wall == CardinalDirection.south:
            painting_position["z"] = self.scene_bounds.rooms[region.region].z_min + depth
            rotation = 0
        elif wall == CardinalDirection.west:
            painting_position["x"] = self.scene_bounds.rooms[region.region].x_min + depth
            rotation = 90
        elif wall == CardinalDirection.east:
            painting_position["x"] = self.scene_bounds.rooms[region.region].x_max - depth
            rotation = 270
        else:
            raise Exception(wall)
        # Set the y coordinate between 1.1 and the height of the room minus the height of the painting.
        painting_position["y"] = float(self.rng.uniform(1.1, self.scene_bounds.rooms[region.region].bounds[1] - extents[1]))
        # Add the painting.
        self.commands.extend(Controller.get_add_physics_object(model_name=record.name,
                                                               object_id=Controller.get_unique_id(),
                                                               position=painting_position,
                                                               rotation={"x": 0, "y": rotation, "z": 0},
                                                               library="models_core.json",
                                                               kinematic=True))

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
                                                               position=self._get_position_along_wall(region=region.region,
                                                                                                      position=position,
                                                                                                      wall=wall,
                                                                                                      depth=depth,
                                                                                                      model_name=record.name),
                                                               rotation={"x": 0, "y": rotation, "z": 0},
                                                               library="models_core.json",
                                                               kinematic=True))

    def _add_stool(self, record: ModelRecord, position: Dict[str, float], wall: CardinalDirection,
                   direction: CardinalDirection, region: RegionWalls) -> None:
        """
        Add a stool to the scene.

        :param record: The model record.
        :param position: The position of the root object.
        :param wall: The wall the kitchen counter is on.
        :param direction: The direction of the lateral arrangement.
        :param region: The `RegionWalls` data.
        """

        self.commands.extend(Controller.get_add_physics_object(model_name=record.name,
                                                               object_id=Controller.get_unique_id(),
                                                               position={k: v for k, v in position.items()},
                                                               rotation={"x": 0, "y": self.rng.uniform(0, 360), "z": 0},
                                                               library="models_core.json",
                                                               kinematic=False))

    def _add_suitcase(self, record: ModelRecord, position: Dict[str, float], wall: CardinalDirection,
                      direction: CardinalDirection, region: RegionWalls) -> None:
        """
        Add a suitcase to the scene.

        :param record: The model record.
        :param position: The position of the root object.
        :param wall: The wall the kitchen counter is on.
        :param direction: The direction of the lateral arrangement.
        :param region: The `RegionWalls` data.
        """

        rotation = ProcGenKitchen.OBJECT_ROTATIONS[record.name][wall.name]
        self.commands.extend(Controller.get_add_physics_object(model_name=record.name,
                                                               object_id=Controller.get_unique_id(),
                                                               position={k: v for k, v in position.items()},
                                                               rotation={"x": 0, "y": rotation, "z": 0},
                                                               library="models_core.json",
                                                               kinematic=False))

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
                                                               position=self._get_position_along_wall(region=region.region,
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
