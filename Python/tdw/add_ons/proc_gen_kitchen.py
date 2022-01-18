from pathlib import Path
from pkg_resources import resource_filename
from enum import Enum
from json import loads
from typing import List, Dict, Optional, Tuple
import numpy as np
from scipy.signal import convolve2d
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.proc_gen_objects import ProcGenObjects
from tdw.cardinal_direction import CardinalDirection
from tdw.ordinal_direction import OrdinalDirection
from tdw.librarian import ModelRecord


class _GenerationState(Enum):
    """
    Enum values used to track the generation state.
    """

    start = 0
    adding_initial_objects = 3
    adding_secondary_objects = 4
    done = 5


class ProcGenKitchen(ProcGenObjects):
    """
    (TODO)
    """

    """:class_var
    Categories of models that can be placed on a shelf.
    """
    ON_SHELF: List[str] = Path(resource_filename(__name__, "proc_gen_kitchen_data/categories_on_shelf.txt")).read_text().split("\n")
    """:class_var
    Data for shelves. Key = model name. Value = Dictionary: "size" (a 2-element list), "ys" (list of shelf y's).
    """
    SHELF_DIMENSIONS: Dict[str, dict] = loads(Path(resource_filename(__name__, "proc_gen_kitchen_data/shelf_dimensions.json")).read_text())
    """:class_var
    The number of chairs around kitchen tables. Key = The number as a string. Value = A list of model names.
    """
    NUMBER_OF_CHAIRS_AROUND_TABLE: Dict[str, List[str]] = loads(Path(resource_filename(__name__, "proc_gen_kitchen_data/chairs_around_tables.json")).read_text())
    """:class_var
    The length of one side of the floating kitchen counter top.
    """
    KITCHEN_COUNTER_TOP_SIZE: float = 0.6096
    _SECONDARY_CATEGORIES: List[str] = ["floor_lamp", "side_table", "basket"]
    """:class_var
    The y value (height) of the wall cabinets.
    """
    WALL_CABINET_Y: float = 1.289581
    """:class_var
    Dictionary: The name of a kitchen counter model, and its corresponding wall cabinet.
    """
    COUNTERS_AND_CABINETS: Dict[str, str] = loads(Path(resource_filename(__name__, "proc_gen_kitchen_data/counters_and_cabinets.json")).read_text())
    """:class_var
    Categories of models that are tall and might obscure windows.
    """
    TALL_CATEGORIES: List[str] = ["refrigerator", "shelf"]

    def __init__(self, random_seed: int = None):
        super().__init__(random_seed=random_seed)
        self._counter_top_material: str = ""
        """:field
        The name of the scene. This will be chosen randomly during scene generation.
        """
        self.scene_name: str = ""
        """:field
        If True, the scene is still being generated. This will remain True for several `communicate()` calls.
        """
        self.generating: bool = True
        self._state: _GenerationState = _GenerationState.start

    def get_initialization_commands(self) -> List[dict]:
        self.generating = True
        self._state = _GenerationState.start
        # Set the wood type and counter top visual material.
        kitchen_counter_wood_type = self.rng.choice(["white_wood", "wood_beach_honey"])
        kitchen_counters = ProcGenObjects.MODEL_CATEGORIES["kitchen_counter"]
        ProcGenObjects.MODEL_CATEGORIES["kitchen_counter"] = [k for k in kitchen_counters if kitchen_counter_wood_type in k]
        kitchen_cabinets = ProcGenObjects.MODEL_CATEGORIES["wall_cabinet"]
        ProcGenObjects.MODEL_CATEGORIES["wall_cabinet"] = [k for k in kitchen_cabinets if kitchen_counter_wood_type in k]
        if kitchen_counter_wood_type == "white_wood":
            self._counter_top_material = "granite_beige_french"
        else:
            self._counter_top_material = "granite_black"
        return super().get_initialization_commands()

    def on_send(self, resp: List[bytes]) -> None:
        super().on_send(resp=resp)
        # Parse the raycast data and add the initial objects.
        if self._state == _GenerationState.start:
            self._add_initial_objects()
        # Add secondary objects.
        elif self._state == _GenerationState.adding_initial_objects:
            self._add_secondary_objects()

    def _add_secondary_objects(self, region: int) -> None:
        """
        Add "secondary objects" in unoccupied spaces around the edges of the room.

        :param region: The index of the region in `self.scene_bounds.rooms`.
        """

        # Get the unoccupied edges of the occupancy map.
        # Source: https://stackoverflow.com/a/41202798
        k = np.ones((3, 3), dtype=int)
        q = convolve2d(self.occupancy_map, k, 'same') < 0
        # noinspection PyPep8
        self.occupancy_map[(q == True) & (self.occupancy_map == 0)] = 9
        positions: List[Tuple[float, float]] = list()
        for ix, iy in np.ndindex(self.occupancy_map.shape):
            x, z = self.get_occupancy_position(ix, iy)
            if self.occupancy_map[ix][iy] == 9 and self.scene_bounds.rooms[region].is_inside(x, z):
                positions.append((x, z))
        for position in positions:
            p = {"x": position[0] + self.rng.uniform(-0.05, 0.05),
                 "y": 0,
                 "z": position[1] + self.rng.uniform(-0.05, 0.05)}
            # Skip most of the positions.
            if self.rng.random() > 0.125:
                continue
            # Choose a random category.
            category = ProcGenKitchen._SECONDARY_CATEGORIES[self.rng.randint(0, len(ProcGenKitchen._SECONDARY_CATEGORIES))]
            if category == "side_table":
                if self.rng.random() < 0.5:
                    rotation = 90
                else:
                    rotation = 0
            else:
                rotation = self.rng.uniform(0, 360)
            model_name = ProcGenObjects.MODEL_CATEGORIES[category][
                self.rng.randint(0, len(ProcGenObjects.MODEL_CATEGORIES[category]))]
            record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(model_name)
            if not self.model_fits_in_region(record=record, position=p, region=region):
                continue
            self.commands.extend(Controller.get_add_physics_object(model_name=model_name,
                                                                   object_id=Controller.get_unique_id(),
                                                                   position=p,
                                                                   rotation={"x": 0, "y": rotation, "z": 0},
                                                                   library="models_core.json",
                                                                   kinematic=True))
            # Add items in the basket.
            if category == "basket":
                extents = TDWUtils.get_bounds_extents(bounds=record.bounds)
                d = extents[0] if extents[0] < extents[2] else extents[2]
                d *= 0.6
                r = d / 2
                y = extents[1]
                model_names = ["vase_02", "jug04", "jug05"]
                for i in range(2, self.rng.randint(4, 6)):
                    model_name = model_names[self.rng.randint(0, len(model_names))]
                    q = TDWUtils.get_random_point_in_circle(center=np.array([p["x"], y, p["z"]]),
                                                            radius=r)
                    q[1] = y
                    self.commands.extend(Controller.get_add_physics_object(model_name=model_name,
                                                                           object_id=Controller.get_unique_id(),
                                                                           position=TDWUtils.array_to_vector3(q),
                                                                           rotation={"x": float(self.rng.uniform(0, 360)),
                                                                                     "y": float(self.rng.uniform(0, 360)),
                                                                                     "z": float(self.rng.uniform(0, 360))},
                                                                           library="models_core.json",
                                                                           scale_factor={"x": 0.5, "y": 0.5, "z": 0.5}))
                    y += 0.25
        # Set kinematic objects.
        self._state = _GenerationState.done
        self.generating = False
        # Generate the final occupancy map.
        self.generate()
        # Request static object data.
        self.commands.append({"$type": "send_composite_objects",
                              "frequency": "once"})

    def _add_initial_objects(self) -> None:
        """
        Create the kitchen. Add kitchen appliances, counter tops, etc. and a table. Objects will be placed on surfaces.
        """

        # Add the work triangle.
        used_walls = self._add_work_triangle()
        # Add the table.
        self._add_table(used_walls=used_walls)
        # Set the state.
        self._state = _GenerationState.adding_initial_objects
        # Generate an occupancy map for the secondary objects.
        self.generate()

    def _add_table(self, used_walls: List[CardinalDirection], table_settings: bool = True,
                   plate_model_name: str = None, fork_model_name: str = None, knife_model_name: str = None,
                   spoon_model_name: str = None, centerpiece_model_name: str = None) -> Optional[ModelRecord]:
        """
        Add a kitchen table with chairs around it.
        Optionally, add forks, knives, spoons, coasters, and cups.
        The plates sometimes have food on them.
        Sometimes, there is a large object (i.e. a bowl or jug) in the center of the table.

        :param used_walls: The walls used in the work triangle. This is used to offset the table position.
        :param table_settings: If True, add tables settings (plates, forks, knives, etc.) in front of each chair.
        :param plate_model_name: If not None, this is the model name of the plates. If None, the plate is `plate06`.
        :param fork_model_name: If not None, this is the model name of the forks. If None, the model name of the forks is random (all fork objects use the same model).
        :param knife_model_name: If not None, this is the model name of the knives. If None, the model name of the knives is random (all knife objects use the same model).
        :param spoon_model_name: If not None, this is the model name of the spoons. If None, the model name of the spoons is random (all spoon objects use the same model).
        :param centerpiece_model_name: If not None, this is the model name of the centerpiece. If None, the model name of the centerpiece is random.

        :return: The model record of the root object. If no models were added to the scene, this is None.
        """

        if plate_model_name is None:
            plate_model_name = "plate06"
        if fork_model_name is None:
            forks = ProcGenObjects.MODEL_CATEGORIES["fork"]
            fork_model_name = forks[self.rng.randint(0, len(forks))]
        if knife_model_name is None:
            knives = ProcGenObjects.MODEL_CATEGORIES["knife"]
            knife_model_name = knives[self.rng.randint(0, len(knives))]
        if spoon_model_name is None:
            spoons = ProcGenObjects.MODEL_CATEGORIES["spoon"]
            spoon_model_name = spoons[self.rng.randint(0, len(spoons))]
        if centerpiece_model_name is None:
            centerpiece_categories = ["jug", "vase", "bowl"]
            centerpiece_category = centerpiece_categories[self.rng.randint(0, len(centerpiece_categories))]
            centerpieces = ProcGenObjects.MODEL_CATEGORIES[centerpiece_category]
            centerpiece_model_name = centerpieces[self.rng.randint(0, len(centerpieces))]
        # Get the position of the table.
        room_center = self.scene_bounds.rooms[self._region].center
        position = {"x": room_center[0] + self.rng.uniform(-0.1, 0.1),
                    "y": 0,
                    "z": room_center[2] + self.rng.uniform(-0.1, 0.1)}
        # Apply offsets.
        offset_distance = 0.1
        if CardinalDirection.north in used_walls:
            position["z"] -= offset_distance
        if CardinalDirection.south in used_walls:
            position["z"] += offset_distance
        if CardinalDirection.east in used_walls:
            position["x"] -= offset_distance
        if CardinalDirection.west in used_walls:
            position["x"] += offset_distance
        rotation = self.rng.uniform(-10, 10)
        # Add the table.
        root_object_id = Controller.get_unique_id()
        tables = ProcGenObjects.MODEL_CATEGORIES["kitchen_table"]
        table_model_name = tables[self.rng.randint(0, len(tables))]
        record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(table_model_name)
        self.commands.extend(Controller.get_add_physics_object(model_name=table_model_name,
                                                               position=position,
                                                               object_id=root_object_id,
                                                               library="models_core.json"))
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
        chairs = ProcGenObjects.MODEL_CATEGORIES["chair"]
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
        if self.rng.random() < 0.75:
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
        self.add_rotation_commands(parent_object_id=root_object_id,
                                   child_object_ids=child_object_ids,
                                   rotation=rotation)
        return record

    def _add_shelf(self, record: ModelRecord, position: Dict[str, float], face_away_from: CardinalDirection) -> None:
        """
        Procedurally generate a shelf with objects on each shelf.

        :param record: The model record.
        :param position: The position of the root object as either a numpy array or a dictionary.
        :param face_away_from: The direction that the object is facing away from. For example, if this is `north`, then the object is looking southwards.

        :return: The model record of the root object. If no models were added to the scene, this is None.
        """

        if face_away_from == CardinalDirection.north:
            rotation: int = 270
        elif face_away_from == CardinalDirection.south:
            rotation = 90
        elif face_away_from == CardinalDirection.west:
            rotation = 0
        elif face_away_from == CardinalDirection.east:
            rotation = 180
        else:
            raise Exception(face_away_from)
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
        self.add_rotation_commands(parent_object_id=root_object_id,
                                   child_object_ids=child_object_ids,
                                   rotation=rotation)

    def _add_kitchen_counter(self, record: ModelRecord, position: Dict[str, float],
                             face_away_from: CardinalDirection, region: int, walls_with_windows: int) -> None:
        """
        Procedurally generate a kitchen counter with objects on it.
        Sometimes, a kitchen counter will have a microwave, which can have objects on top of it.
        There will never be more than 1 microwave in the scene.

        :param record: The model record.
        :param position: The position of the root object as either a numpy array or a dictionary.
        :param face_away_from: The direction that the object is facing away from. For example, if this is `north`, then the object is looking southwards.
        :param region: The index of the region in `self.scene_bounds.rooms`.
        :param walls_with_windows: Bitwise sum of walls with windows.

        :return: The model record of the root object. If no models were added to the scene, this is None.
        """

        if face_away_from == CardinalDirection.north:
            rotation: int = 0
        elif face_away_from == CardinalDirection.south:
            rotation = 180
        elif face_away_from == CardinalDirection.west:
            rotation = 270
        elif face_away_from == CardinalDirection.east:
            rotation = 90
        else:
            raise Exception(face_away_from)
        extents = TDWUtils.get_bounds_extents(bounds=record.bounds)
        # Add objects on the kitchen counter.
        if extents[0] < 0.7 or "microwave" in self._used_unique_categories:
            self.add_object_with_other_objects_on_top(record=record,
                                                      position={k: v for k, v in position.items()},
                                                      rotation=rotation,
                                                      category="kitchen_counter")
            # Add a wall cabinet if one exists and there is no window here.
            if record.name in ProcGenKitchen.COUNTERS_AND_CABINETS and walls_with_windows & face_away_from.value == 0:
                wall_cabinet_model_name = ProcGenKitchen.COUNTERS_AND_CABINETS[record.name]
                wall_cabinet_record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(wall_cabinet_model_name)
                wall_cabinet_extents = TDWUtils.get_bounds_extents(bounds=wall_cabinet_record.bounds)
                room = self.scene_bounds.rooms[region]
                if face_away_from == CardinalDirection.north:
                    wall_cabinet_position = {"x": position["x"],
                                             "y": ProcGenKitchen.WALL_CABINET_Y,
                                             "z": room.z_max - wall_cabinet_extents[2] / 2}
                elif face_away_from == CardinalDirection.south:
                    wall_cabinet_position = {"x": position["x"],
                                             "y": ProcGenKitchen.WALL_CABINET_Y,
                                             "z": room.z_min + wall_cabinet_extents[2] / 2}
                elif face_away_from == CardinalDirection.west:
                    wall_cabinet_position = {"x": room.x_max - wall_cabinet_extents[2] / 2,
                                             "y": ProcGenKitchen.WALL_CABINET_Y,
                                             "z": position["z"]}
                elif face_away_from == CardinalDirection.east:
                    wall_cabinet_position = {"x": room.x_min - wall_cabinet_extents[2] / 2,
                                             "y": ProcGenKitchen.WALL_CABINET_Y,
                                             "z": position["z"]}
                else:
                    raise Exception(face_away_from)
                self.commands.extend(Controller.get_add_physics_object(
                    model_name=ProcGenKitchen.COUNTERS_AND_CABINETS[record.name],
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
                                                                   position={k: v for k, v in position.items()},
                                                                   rotation={"x": 0, "y": rotation, "z": 0},
                                                                   library="models_core.json",
                                                                   kinematic=True))
            # Get the top position of the kitchen counter.
            object_top = {"x": position["x"],
                          "y": record.bounds["top"]["y"] + position["y"],
                          "z": position["z"]}
            microwave_model_names = ProcGenObjects.MODEL_CATEGORIES["microwave"]
            microwave_model_name = microwave_model_names[self.rng.randint(0, len(microwave_model_names))]
            microwave_record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(microwave_model_name)
            # Add a microwave and add objects on top of the microwave.
            self.add_object_with_other_objects_on_top(record=microwave_record,
                                                      position=object_top,
                                                      rotation=rotation - 180,
                                                      category="microwave")
            self._used_unique_categories.append("microwave")

    def _add_refrigerator(self, record: ModelRecord, position: Dict[str, float],
                          face_away_from: CardinalDirection) -> None:
        """
        Procedurally generate a refrigerator.

        :param record: The model record.
        :param position: The position.
        :param face_away_from: The direction that the object is facing away from. For example, if this is `north`, then the object is looking southwards.

        :return: The model record of the root object. If no models were added to the scene, this is None.
        """

        if face_away_from == CardinalDirection.north:
            rotation: int = 180
        elif face_away_from == CardinalDirection.south:
            rotation = 0
        elif face_away_from == CardinalDirection.west:
            rotation = 90
        elif face_away_from == CardinalDirection.east:
            rotation = 270
        else:
            raise Exception(face_away_from)
        self.commands.extend(Controller.get_add_physics_object(model_name=record.name,
                                                               object_id=Controller.get_unique_id(),
                                                               position={k: v for k, v in position.items()},
                                                               rotation={"x": 0, "y": rotation, "z": 0},
                                                               library="models_core.json",
                                                               kinematic=True))

    def _add_dishwasher(self, record: ModelRecord, position: Dict[str, float],
                        face_away_from: CardinalDirection) -> None:
        """
        Procedurally generate a dishwasher.

        :param record: The model record.
        :param position: The position.
        :param face_away_from: The direction that the object is facing away from. For example, if this is `north`, then the object is looking southwards.

        :return: The model record of the root object. If no models were added to the scene, this is None.
        """

        if face_away_from == CardinalDirection.north:
            rotation: int = 180
        elif face_away_from == CardinalDirection.south:
            rotation = 0
        elif face_away_from == CardinalDirection.west:
            rotation = 90
        elif face_away_from == CardinalDirection.east:
            rotation = 270
        else:
            raise Exception(face_away_from)
        # Add the dishwasher.
        self.commands.extend(Controller.get_add_physics_object(model_name=record.name,
                                                               object_id=Controller.get_unique_id(),
                                                               position={k: v for k, v in position.items()},
                                                               rotation={"x": 0, "y": rotation, "z": 0},
                                                               library="models_core.json",
                                                               kinematic=True))
        # Add a kitchen counter top.
        extents = TDWUtils.get_bounds_extents(bounds=record.bounds)
        if face_away_from == CardinalDirection.west or face_away_from == CardinalDirection.east:
            size = (extents[2], extents[0])
        else:
            size = (extents[0], extents[2])
        self._add_kitchen_counter_top(position={k: v for k, v in position.items()}, size=size)

    def _add_stove(self, record: ModelRecord, position: Dict[str, float], face_away_from: CardinalDirection) -> None:
        """
        Procedurally generate a stove with objects on it.

        :param record: The model record.
        :param position: The position of the root object as either a numpy array or a dictionary.
        :param face_away_from: The direction that the object is facing away from. For example, if this is `north`, then the object is looking southwards.

        :return: The model record of the root object. If no models were added to the scene, this is None.
        """

        if face_away_from == CardinalDirection.north:
            rotation: int = 90
        elif face_away_from == CardinalDirection.south:
            rotation = 270
        elif face_away_from == CardinalDirection.west:
            rotation = 180
        elif face_away_from == CardinalDirection.east:
            rotation = 0
        else:
            raise Exception(face_away_from)
        return self.add_object_with_other_objects_on_top(record=record,
                                                         position={k: v for k, v in position.items()},
                                                         rotation=rotation,
                                                         category="stove")

    def _add_kitchen_counter_top(self, position: Dict[str, float], size: Tuple[float, float] = None) -> None:
        """
        Add a floating (kinematic) kitchen counter top to the scene.

        :param position: The position of the kitchen counter top. The y coordinate will be adjusted to be 0.9.
        :param size: If not None, this is the (x, z) size of the counter top.
        """

        if size is None:
            scale_factor = {"x": ProcGenKitchen.KITCHEN_COUNTER_TOP_SIZE,
                            "y": 0.0371,
                            "z": ProcGenKitchen.KITCHEN_COUNTER_TOP_SIZE}
        else:
            scale_factor = {"x": size[0],
                            "y": 0.0371,
                            "z": size[1]}
        object_id = Controller.get_unique_id()
        self.commands.extend([{"$type": "load_primitive_from_resources",
                               "primitive_type": "Cube",
                               "id": object_id,
                               "position": {"x": position["x"], "y": 0.9, "z": position["z"]},
                               "orientation": {"x": 0, "y": 0, "z": 0}},
                              Controller.get_add_material(self._counter_top_material, "materials_low.json"),
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
        self.add_rectangular_arrangement(size=(ProcGenKitchen.KITCHEN_COUNTER_TOP_SIZE * 0.8,
                                               ProcGenKitchen.KITCHEN_COUNTER_TOP_SIZE * 0.8),
                                         position={"x": position["x"], "y": 0.9167836, "z": position["z"]},
                                         categories=ProcGenObjects._VERTICAL_SPATIAL_RELATIONS["on_top_of"]["kitchen_counter"])

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

    def _add_lateral_arrangement(self, position: Dict[str, float], categories: List[str], direction: CardinalDirection,
                                 face_away_from: CardinalDirection, length: float, region: int, walls_with_windows: int) -> None:
        """
        Create a linear arrangement of objects, each one adjacent to the next.
        The objects can have other objects on top of them.

        :param position: The position of the root object as either a numpy array or a dictionary.
        :param face_away_from: The direction that the object is facing away from. For example, if this is `north`, then the object is looking southwards.
        :param categories: The ordered list of categories. An object at index 0 will be added first, then index 1, etc.
        :param direction: The direction that the lateral arrangement will extent toward.
        :param length: The maximum length of the lateral arrangement.
        :param region: The index of the region in `self.scene_bounds.rooms`.
        :param walls_with_windows: Bitwise sum of walls with windows.
        """

        def __add_half_extent_to_position() -> Dict[str, float]:
            ex = ProcGenObjects._get_lateral_length(model_name=model_name)
            if direction == CardinalDirection.north:
                position["z"] += ex / 2
            elif direction == CardinalDirection.south:
                position["z"] -= ex / 2
            elif direction == CardinalDirection.east:
                position["x"] += ex / 2
            elif direction == CardinalDirection.west:
                position["x"] -= ex / 2
            else:
                raise Exception(direction)
            return position

        distance = 0
        for category in categories:
            # Add a floating kitchen counter top.
            if category == "floating_kitchen_counter_top":
                self._add_kitchen_counter_top(position=position)
                extent = ProcGenKitchen.KITCHEN_COUNTER_TOP_SIZE / 2
                if direction == CardinalDirection.north:
                    position["z"] += extent
                elif direction == CardinalDirection.south:
                    position["z"] -= extent
                elif direction == CardinalDirection.east:
                    position["x"] += extent
                elif direction == CardinalDirection.west:
                    position["x"] -= extent
                else:
                    raise Exception(direction)
                continue
            # Remove tall objects from walls with windows.
            if walls_with_windows & face_away_from.value != 0 and category in ProcGenKitchen.TALL_CATEGORIES:
                c = "kitchen_counter"
            else:
                c = category
            # Choose a random starting object.
            model_names = ProcGenObjects.MODEL_CATEGORIES[c][:]
            self.rng.shuffle(model_names)
            model_name = ""
            got_model_name = False
            for m in model_names:
                extent = ProcGenObjects._get_lateral_length(model_name=m)
                # The model must fit within the distance of the lateral arrangement.
                if distance + extent < length:
                    got_model_name = True
                    model_name = m
                    distance += extent
                    break
            if not got_model_name:
                return
            # Add half of the long extent to the position.
            position = __add_half_extent_to_position()
            # Out of bounds. Stop here.
            if not self.scene_bounds.rooms[region].is_inside(position["x"], position["z"]):
                break
            # Get the record.
            record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(model_name)
            # Add the objects.
            if c == "kitchen_counter":
                self._add_kitchen_counter(record=record, position=position, face_away_from=face_away_from,
                                          region=region, walls_with_windows=walls_with_windows)
                position = __add_half_extent_to_position()
            elif c == "shelf":
                self._add_shelf(record=record, position=position, face_away_from=face_away_from)
                position = __add_half_extent_to_position()
            elif c == "refrigerator":
                self._add_refrigerator(record=record, position=position, face_away_from=face_away_from)
                position = __add_half_extent_to_position()
            elif c == "dishwasher":
                self._add_dishwasher(record=record, position=position, face_away_from=face_away_from)
                position = __add_half_extent_to_position()
            elif c == "stove":
                self._add_stove(record=record, position=position, face_away_from=face_away_from)
                position = __add_half_extent_to_position()
            else:
                print(c)
                self._add_kitchen_counter(record=record, position=position, face_away_from=face_away_from,
                                          region=region, walls_with_windows=walls_with_windows)
                position = __add_half_extent_to_position()

    def _get_longer_walls(self, region: int) -> Tuple[List[CardinalDirection], float]:
        """
        :param region: The index of the region in `self.scene_bounds.rooms`.

        :return: Tuple: A list of the longer walls, the length of the wall.
        """

        room = self.scene_bounds.rooms[region]
        x = room.x_max - room.x_min
        z = room.z_max - room.z_min
        if x < z:
            return [CardinalDirection.west, CardinalDirection.east], z
        else:
            return [CardinalDirection.north, CardinalDirection.south], x

    def _get_shorter_walls(self, region: int) -> Tuple[List[CardinalDirection], float]:
        """
        :param region: The index of the region in `self.scene_bounds.rooms`.

        :return: Tuple: A list of the shorter walls, the length of the wall.
        """

        room = self.scene_bounds.rooms[region]
        x = room.x_max - room.x_min
        z = room.z_max - room.z_min
        if x > z:
            return [CardinalDirection.west, CardinalDirection.east], z
        else:
            return [CardinalDirection.north, CardinalDirection.south], x

    @staticmethod
    def _get_corners_from_wall(wall: CardinalDirection) -> List[OrdinalDirection]:
        """
        :param wall: The wall.

        :return: The corners of the wall.
        """

        if wall == CardinalDirection.north:
            return [OrdinalDirection.northwest, OrdinalDirection.northeast]
        elif wall == CardinalDirection.south:
            return [OrdinalDirection.southwest, OrdinalDirection.southeast]
        elif wall == CardinalDirection.west:
            return [OrdinalDirection.northwest, OrdinalDirection.southwest]
        elif wall == CardinalDirection.east:
            return [OrdinalDirection.northeast, OrdinalDirection.southeast]

    def _get_corner_position(self, corner: OrdinalDirection, region: int) -> Dict[str, float]:
        """
        :param corner: The corner.
        :param region: The index of the region in `self.scene_bounds.rooms`.

        :return: The position of an object in the corner of the room.
        """

        room = self.scene_bounds.rooms[region]
        s = ProcGenKitchen.KITCHEN_COUNTER_TOP_SIZE / 2
        if corner == OrdinalDirection.northwest:
            return {"x": room.x_min + s,
                    "y": 0,
                    "z": room.z_max - s}
        elif corner == OrdinalDirection.northeast:
            return {"x": room.x_max - s,
                    "y": 0,
                    "z": room.z_max - s}
        elif corner == OrdinalDirection.southwest:
            return {"x": room.x_min + s,
                    "y": 0,
                    "z": room.z_min + s}
        elif corner == OrdinalDirection.southeast:
            return {"x": room.x_max - s,
                    "y": 0,
                    "z": room.z_min + s}
        else:
            raise Exception(corner)

    @staticmethod
    def _get_position_offset_from_direction(position: Dict[str, float], direction: CardinalDirection) -> Dict[str, float]:
        """
        :param position: The corner position.
        :param direction: The direction.

        :return: The offset position.
        """

        if direction == CardinalDirection.north:
            return {"x": position["x"],
                    "y": position["y"],
                    "z": position["z"] + ProcGenKitchen.KITCHEN_COUNTER_TOP_SIZE / 2}
        elif direction == CardinalDirection.south:
            return {"x": position["x"],
                    "y": position["y"],
                    "z": position["z"] - ProcGenKitchen.KITCHEN_COUNTER_TOP_SIZE / 2}
        elif direction == CardinalDirection.west:
            return {"x": position["x"] - ProcGenKitchen.KITCHEN_COUNTER_TOP_SIZE / 2,
                    "y": position["y"],
                    "z": position["z"]}
        elif direction == CardinalDirection.east:
            return {"x": position["x"] + ProcGenKitchen.KITCHEN_COUNTER_TOP_SIZE / 2,
                    "y": position["y"],
                    "z": position["z"]}
        raise Exception(direction)

    @staticmethod
    def _get_directions_from_corner(corner: OrdinalDirection, wall: CardinalDirection) -> Tuple[CardinalDirection, CardinalDirection]:
        """
        :param corner: The corner.

        :return: Tuple: direction, face_away_from
        """

        if corner == OrdinalDirection.northwest:
            if wall == CardinalDirection.north:
                return CardinalDirection.east, CardinalDirection.north
            elif wall == CardinalDirection.west:
                return CardinalDirection.south, CardinalDirection.west
        elif corner == OrdinalDirection.northeast:
            if wall == CardinalDirection.north:
                return CardinalDirection.west, CardinalDirection.north
            elif wall == CardinalDirection.east:
                return CardinalDirection.south, CardinalDirection.east
        elif corner == OrdinalDirection.southwest:
            if wall == CardinalDirection.south:
                return CardinalDirection.east, CardinalDirection.south
            elif wall == CardinalDirection.west:
                return CardinalDirection.north, CardinalDirection.west
        elif corner == OrdinalDirection.southeast:
            if wall == CardinalDirection.south:
                return CardinalDirection.west, CardinalDirection.south
            elif wall == CardinalDirection.east:
                return CardinalDirection.north, CardinalDirection.east
        raise Exception(corner, wall)

    def _add_work_triangle(self, region: int, non_continuous_walls: int, walls_with_windows: int) -> List[CardinalDirection]:
        """
        Add a kitchen work triangle of counters and appliances.
        Source: https://kbcrate.com/kitchen-design-kitchen-work-triangle-improve-workspace/

        :param region: The index of the region in `self.scene_bounds.rooms`.
        :param non_continuous_walls: Bitwise sum of non-continuous walls.
        :param walls_with_windows: Bitwise sum of walls with windows.

        :return: A list of unused walls.
        """

        longer_walls, length = self._get_longer_walls(region=region)
        longer_walls_ok = True
        for w in longer_walls:
            if non_continuous_walls & w.value == 0:
                longer_walls_ok = False
                break
        triangles = [self._add_straight_work_triangle, self._add_l_work_triangle]
        if longer_walls_ok:
            triangles.append(self._add_parallel_work_triangle)
        shorter_walls, length = self._get_shorter_walls(region=region)
        shorter_walls_ok = True
        for w in shorter_walls:
            if non_continuous_walls & w.value == 0:
                shorter_walls_ok = False
                break
        if shorter_walls_ok:
            triangles.append(self._add_u_work_triangle)
        return self.rng.choice(triangles)(region=region, walls_with_windows=walls_with_windows)

    def _add_straight_work_triangle(self, region: int, non_continuous_walls: int,
                                    walls_with_windows: int) -> List[CardinalDirection]:
        """
        Add a lateral arrangement of kitchen counters and appliances along one of the longer walls.

        :param region: The index of the region in `self.scene_bounds.rooms`.
        :param non_continuous_walls: Bitwise sum of non-continuous walls.
        :param walls_with_windows: Bitwise sum of walls with windows.

        :return: A list of unused walls.
        """

        longer_walls, length = self._get_longer_walls(region=region)
        longer_wall = self._get_wall(walls=longer_walls, non_continuous_walls=non_continuous_walls)
        corners = self._get_corners_from_wall(wall=longer_wall)
        corner = corners[self.rng.randint(0, len(corners))]
        position = self._get_corner_position(corner=corner, region=region)
        direction, face_away_from = self._get_directions_from_corner(corner=corner, wall=longer_wall)
        categories = ["refrigerator", "dishwasher", "sink", "kitchen_counter", "stove", "kitchen_counter", "shelf"]
        if self.rng.random() < 0.5:
            categories.reverse()
        self._add_lateral_arrangement(position=position, direction=direction, face_away_from=face_away_from,
                                      categories=categories, length=length, region=region,
                                      walls_with_windows=walls_with_windows)
        walls = [c for c in CardinalDirection]
        walls.remove(longer_wall)
        return walls

    def _add_parallel_work_triangle(self, region: int, non_continuous_walls: int,
                                    walls_with_windows: int) -> List[CardinalDirection]:
        """
        Add two lateral arrangements of kitchen counters and appliances along each of the longer walls.

        :param region: The index of the region in `self.scene_bounds.rooms`.
        :param non_continuous_walls: Bitwise sum of non-continuous walls.
        :param walls_with_windows: Bitwise sum of walls with windows.

        :return: A list of unused walls.
        """

        longer_walls, length = self._get_longer_walls(region=region)
        self.rng.shuffle(longer_walls)
        for wall, categories in zip(longer_walls, [["kitchen_counter", "stove", "kitchen_counter", "kitchen_counter", "kitchen_counter"],
                                                   ["refrigerator", "dishwasher", "sink", "kitchen_counter", "kitchen_counter"]]):
            if self.rng.random() < 0.5:
                categories.reverse()
            corners = self._get_corners_from_wall(wall=wall)
            corner = corners[self.rng.randint(0, len(corners))]
            position = self._get_corner_position(corner=corner, region=region)
            direction, face_away_from = self._get_directions_from_corner(corner=corner, wall=wall)
            self._add_lateral_arrangement(position=position, direction=direction, face_away_from=face_away_from,
                                          categories=categories, length=length, region=region,
                                          walls_with_windows=walls_with_windows)
        shorter_walls, length = self._get_shorter_walls(region=region)
        return shorter_walls

    def _add_l_work_triangle(self, region: int, non_continuous_walls: int,
                             walls_with_windows: int) -> List[CardinalDirection]:
        """
        Add an L shape of two lateral arrangements of kitchen counters and appliances, one along one of the longer walls and one along one of the shorter walls.

        :param region: The index of the region in `self.scene_bounds.rooms`.
        :param non_continuous_walls: Bitwise sum of non-continuous walls.
        :param walls_with_windows: Bitwise sum of walls with windows.

        :return: A list of unused walls.
        """

        longer_walls, length = self._get_longer_walls(region=region)
        longer_wall = self._get_wall(walls=longer_walls, non_continuous_walls=non_continuous_walls)
        corners = self._get_corners_from_wall(wall=longer_wall)
        corner = corners[self.rng.randint(0, len(corners))]
        position = self._get_corner_position(corner=corner, region=region)
        direction, face_away_from = self._get_directions_from_corner(corner=corner, wall=longer_wall)
        categories = ["floating_kitchen_counter_top", "sink", "dishwasher", "stove", "kitchen_counter", "shelf"]
        self._add_lateral_arrangement(position=position, direction=direction, face_away_from=face_away_from,
                                      categories=categories, length=length, region=region,
                                      walls_with_windows=walls_with_windows)
        # Get the shorter wall.
        shorter_wall = CardinalDirection(corner.value - longer_wall.value)
        # Get the length of the shorter wall.
        shorter_walls, length = self._get_shorter_walls(region=region)
        length -= ProcGenKitchen.KITCHEN_COUNTER_TOP_SIZE
        # Get everything else.
        direction, face_away_from = self._get_directions_from_corner(corner=corner, wall=shorter_wall)
        position = self._get_corner_position(corner=corner, region=region)
        # Offset the position.
        position = self._get_position_offset_from_direction(position=position, direction=direction)
        category_lists = [["kitchen_counter", "kitchen_counter", "refrigerator", "shelf"],
                          ["kitchen_counter", "refrigerator", "kitchen_counter", "shelf"]]
        categories: List[str] = category_lists[self.rng.randint(0, len(category_lists))]
        self._add_lateral_arrangement(position=position, direction=direction, face_away_from=face_away_from,
                                      categories=categories, length=length, region=region,
                                      walls_with_windows=walls_with_windows)
        walls = [c for c in CardinalDirection]
        walls.remove(longer_wall)
        walls.remove(shorter_wall)
        return walls

    def _add_u_work_triangle(self, region: int, non_continuous_walls: int,
                             walls_with_windows: int) -> List[CardinalDirection]:
        """
        Add one long lateral arrangement and two shorter lateral arrangements in a U shape.

        :param region: The index of the region in `self.scene_bounds.rooms`.
        :param non_continuous_walls: Bitwise sum of non-continuous walls.
        :param walls_with_windows: Bitwise sum of walls with windows.

        :return: A list of unused walls.
        """

        # Add the longer wall.
        longer_walls, length = self._get_longer_walls(region=region)
        length -= ProcGenKitchen.KITCHEN_COUNTER_TOP_SIZE
        longer_wall = self._get_wall(walls=longer_walls, non_continuous_walls=non_continuous_walls)
        corners = self._get_corners_from_wall(wall=longer_wall)
        corner = corners[self.rng.randint(0, len(corners))]
        position = self._get_corner_position(corner=corner, region=region)
        direction, face_away_from = self._get_directions_from_corner(corner=corner, wall=longer_wall)
        categories = ["sink", "kitchen_counter", "stove", "kitchen_counter"]
        if self.rng.random() < 0.5:
            categories.reverse()
        categories.insert(0, "floating_kitchen_counter_top")
        # Fill the rest of the lateral arrangement.
        for i in range(20):
            categories.append("kitchen_counter")
        self._add_lateral_arrangement(position=position, direction=direction, face_away_from=face_away_from,
                                      categories=categories, length=length, region=region,
                                      walls_with_windows=walls_with_windows)
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
        opposite_corner_position = self._get_corner_position(corner=opposite_corner, region=region)
        # Add a counter top at the end.
        self._add_kitchen_counter_top(position=opposite_corner_position)
        # Get the length of the shorter wall.
        shorter_walls, length = self._get_shorter_walls(region=region)
        length -= ProcGenKitchen.KITCHEN_COUNTER_TOP_SIZE
        if self.rng.random() < 0.5:
            corners.reverse()
        for corner, categories in zip(corners, [["kitchen_counter", "refrigerator", "kitchen_counter", "shelf"],
                                                ["kitchen_counter", "dishwasher", "kitchen_counter", "kitchen_counter"]]):
            # Get the wall.
            shorter_wall = CardinalDirection(corner.value - longer_wall.value)
            # Get everything else.
            direction, face_away_from = self._get_directions_from_corner(corner=corner, wall=shorter_wall)
            position = self._get_corner_position(corner=corner, region=region)
            # Offset the position.
            position = self._get_position_offset_from_direction(position=position, direction=direction)
            self._add_lateral_arrangement(position=position, direction=direction, face_away_from=face_away_from,
                                          categories=categories, length=length, region=region,
                                          walls_with_windows=walls_with_windows)
        longer_walls.remove(longer_wall)
        return longer_walls

    def _get_wall(self, walls: List[CardinalDirection], non_continuous_walls: int) -> CardinalDirection:
        """
        :param walls: A list of walls.
        :param non_continuous_walls: Bitwise sum of non-continuous walls.

        :return: A valid continuous wall.
        """

        ws = [w for w in walls if non_continuous_walls & w.value == 0]
        if len(ws) == 0:
            raise Exception(non_continuous_walls, walls)
        if len(ws) == 1:
            return ws[0]
        else:
            return ws[self.rng.randint(0, len(ws))]

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
                coasters = ProcGenObjects.MODEL_CATEGORIES["coaster"]
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
            cups = ProcGenObjects.MODEL_CATEGORIES["cup" if self.rng.random() < 0.5 else "wineglass"]
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
            food = ProcGenObjects.MODEL_CATEGORIES[food_category]
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
