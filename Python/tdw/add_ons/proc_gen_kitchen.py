from typing import List, Dict, Optional
import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.proc_gen_objects import ProcGenObjects
from tdw.cardinal_direction import CardinalDirection
from tdw.ordinal_direction import OrdinalDirection
from tdw.librarian import ModelRecord


class ProcGenKitchen(ProcGenObjects):
    # Categories of models that can be on shelves.
    _ON_SHELF: List[str] = ["book", "bottle", "bowl", "candle", "carving_fork", "coaster", "coffee_grinder",
                            "coffee_maker", "coin", "cork", "cup", "fork", "house_plant", "knife", "ladle", "jar",
                            "pan", "pen", "pot", "scissors", "soap_dispenser", "spoon", "tea_tray", "vase"]
    # Data for shelves. Key = model name. Value = Dictionary: "size" (a 2-element list), "ys" (list of shelf y's).
    _SHELVES: Dict[str, dict] = {"4ft_shelf_metal": {"size": [0.9451682, 0.3857702],
                                                     "ys": [0.40797001123428345, 0.8050058484077454,
                                                            1.200427532196045]},
                                 "4ft_wood_shelving": {"size": [0.9451682, 0.3857702],
                                                       "ys": [0.40797001123428345, 0.8050058484077454,
                                                              1.200427532196045]},
                                 "5ft_shelf_metal": {"size": [0.56710092, 0.2314623],
                                                     "ys": [0.33903638,  0.73496544, 1.13089252, 1.51810455]},
                                 "5ft_wood_shelving": {"size": [0.56710092, 0.2314623],
                                                       "ys": [0.33903608, 0.73496497, 1.1308918, 1.51810372]},
                                 "6ft_shelf_metal": {"size": [0.56710068, 0.2314629],
                                                     "ys": [0.23687799, 0.63233, 1.02965903, 1.4213599, 1.81870079]},
                                 "6ft_wood_shelving": {"size": [0.56710068, 0.2314629],
                                                       "ys": [0.23687607, 0.63232845, 1.02965784, 1.42135918,
                                                              1.81870043]}}
    # The shapes of the tables.
    _TABLE_SHAPES: Dict[str, List[str]] = {"rectangle": ["dining_room_table"],
                                           "square_or_circle": ["enzo_industrial_loft_pine_metal_round_dining_table",
                                                                "quatre_dining_table"]}
    _KITCHEN_COUNTER_TOP_SIZE: float = 0.6096

    def __init__(self, random_seed: int = None, region: int = 0):
        super().__init__(random_seed=random_seed)
        self._counter_top_material: str = ""
        self._region: int = region

    def get_initialization_commands(self) -> List[dict]:
        commands = super().get_initialization_commands()
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
        return commands

    def _add_table(self, position: Dict[str, float], rotation: float, table_settings: bool = True,
                   plate_model_name: str = None, fork_model_name: str = None, knife_model_name: str = None,
                   spoon_model_name: str = None, centerpiece_model_name: str = None) -> Optional[ModelRecord]:
        """
        Add a kitchen table with chairs around it.
        Optionally, add forks, knives, spoons, coasters, and cups.
        The plates sometimes have food on them.
        Sometimes, there is a large object (i.e. a bowl or jug) in the center of the table.

        :param position: The position of the root object.
        :param rotation: The root object's rotation in degrees around the y axis; all other objects will be likewise rotated.
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
            centerpiece_categories = ["jug", "vase", "pot", "bowl", "pan"]
            centerpiece_category = centerpiece_categories[self.rng.randint(0, len(centerpiece_categories))]
            centerpieces = ProcGenObjects.MODEL_CATEGORIES[centerpiece_category]
            centerpiece_model_name = centerpieces[self.rng.randint(0, len(centerpieces))]
        # Add the table.
        root_object_id = Controller.get_unique_id()
        tables = ProcGenObjects.MODEL_CATEGORIES["table"]
        table_model_name = tables[self.rng.randint(0, len(tables))]
        record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(table_model_name)
        self.commands.extend(Controller.get_add_physics_object(model_name=table_model_name,
                                                               position=position,
                                                               object_id=root_object_id,
                                                               library="models_core.json"))
        child_object_ids: List[int] = list()
        # Get the shape of the table.
        table_shape = ""
        for shape in ProcGenKitchen._TABLE_SHAPES:
            if record.name in ProcGenKitchen._TABLE_SHAPES[shape]:
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
        if table_shape == "square_or_circle":
            for side in ["left", "right", "front", "back"]:
                chair_bound_points.append(np.array([record.bounds[side]["x"] + position["x"],
                                                    0,
                                                    record.bounds[side]["z"] + position["z"]]))
        # Add chairs around the longer sides of the table.
        else:
            table_extents = TDWUtils.get_bounds_extents(bounds=record.bounds)
            if table_extents[0] > table_extents[2]:
                for side in ["front", "back"]:
                    chair_bound_points.extend([np.array([record.bounds[side]["x"] + position["x"],
                                                         0,
                                                         table_extents[2] * 0.25 + position["z"]]),
                                               np.array([record.bounds[side]["x"] + position["x"],
                                                         0,
                                                         table_extents[2] * 0.75 + position["z"]])])
            else:
                for side in ["left", "right"]:
                    chair_bound_points.extend([np.array([table_extents[0] * 0.25 + position["x"],
                                                         0,
                                                         record.bounds[side]["z"] + position["z"]]),
                                               np.array([table_extents[0] * 0.75 + position["x"],
                                                         0,
                                                         record.bounds[side]["z"] + position["z"]])])
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
            for bound in ["left", "right", "front", "back"]:
                table_bound_point = np.array([record.bounds[bound]["x"] + position["x"],
                                              0,
                                              record.bounds[bound]["z"] + position["z"]])
                # Get a position for the plate.
                # Get the vector towards the center.
                v = np.array([position["x"], position["z"]]) - \
                    np.array([table_bound_point[0], table_bound_point[2]])
                # Get the normalized direction.
                v = v / np.linalg.norm(v)
                # Move the plates inward.
                v *= float(self.rng.uniform(0.15, 0.2))
                # Get a slightly perturbed position.
                plate_position = np.array([float(table_bound_point[0] + v[0] + self.rng.uniform(-0.03, 0.03)),
                                          top_arr[1],
                                          float(table_bound_point[2] + v[1] + self.rng.uniform(-0.03, 0.03))])
                # Add the plate.
                object_id = Controller.get_unique_id()
                child_object_ids.append(object_id)
                self.commands.extend(Controller.get_add_physics_object(model_name=plate_model_name,
                                                                       position=TDWUtils.array_to_vector3(plate_position),
                                                                       object_id=object_id,
                                                                       library="models_core.json"))
                # Get the direction from the plate to the center.
                v = np.array([position["x"], position["z"]]) - \
                    np.array([plate_position[0], plate_position[2]])
                v / np.linalg.norm(v)
                # Get the positions of the fork, knife, and spoon.
                q = v * self.rng.uniform(0.2, 0.3)
                fork_position = np.array([plate_position[0] - q[1] + self.rng.uniform(-0.03, 0.03),
                                          plate_position[1],
                                          plate_position[2] + q[0] + self.rng.uniform(-0.03, 0.03)])
                # Get the knife position.
                q = v * self.rng.uniform(0.2, 0.3)
                knife_position = np.array([plate_position[0] + q[1] + self.rng.uniform(-0.03, 0.03),
                                           plate_position[1],
                                           plate_position[2] - q[0] + self.rng.uniform(-0.03, 0.03)])
                q = v * self.rng.uniform(0.3, 0.4)
                spoon_position = np.array([plate_position[0] + q[1] + self.rng.uniform(-0.03, 0.03),
                                           plate_position[1]])
                # Get the rotation of the fork, knife, and spoon.
                if bound == "left":
                    rotation = 90
                elif bound == "right":
                    rotation = 270
                elif bound == "front":
                    rotation = 180
                else:
                    rotation = 0
                # Add a fork.
                object_id = Controller.get_unique_id()
                child_object_ids.append(object_id)
                self.commands.extend(Controller.get_add_physics_object(model_name=fork_model_name,
                                                                       object_id=object_id,
                                                                       position=TDWUtils.array_to_vector3(fork_position),
                                                                       rotation={"x": 0,
                                                                                 "y": rotation + float(self.rng.uniform(-15, 15)),
                                                                                 "z": 0},
                                                                       library="models_core.json"))
                # Add a knife.
                object_id = Controller.get_unique_id()
                child_object_ids.append(object_id)
                self.commands.extend(Controller.get_add_physics_object(model_name=knife_model_name,
                                                                       object_id=object_id,
                                                                       position=TDWUtils.array_to_vector3(knife_position),
                                                                       rotation={"x": 0,
                                                                                 "y": rotation + float(self.rng.uniform(-15, 15)),
                                                                                 "z": 0},
                                                                       library="models_core.json"))
                # Add a spoon.
                object_id = Controller.get_unique_id()
                child_object_ids.append(object_id)
                self.commands.extend(Controller.get_add_physics_object(model_name=spoon_model_name,
                                                                       object_id=object_id,
                                                                       position=TDWUtils.array_to_vector3(spoon_position),
                                                                       rotation={"x": 0,
                                                                                 "y": rotation + float(self.rng.uniform(-15, 15)),
                                                                                 "z": 0},
                                                                       library="models_core.json"))
                # Add a cup.
                if self.rng.random() > 0.33:
                    # Get the position of the cup.
                    q = v * self.rng.uniform(0.2, 0.3)
                    r = v * self.rng.uniform(0.25, 0.3)
                    cup_position = np.array([plate_position[0] + q[1] + r[0] + self.rng.uniform(-0.03, 0.03),
                                             plate_position[1],
                                             plate_position[2] - q[0] + r[1] + self.rng.uniform(-0.03, 0.03)])
                    # Add a coaster.
                    if self.rng.random() > 0.5:
                        coasters = ProcGenObjects.MODEL_CATEGORIES["coaster"]
                        coaster_model_name: str = coasters[self.rng.randint(0, len(coasters))]
                        object_id = Controller.get_unique_id()
                        child_object_ids.append(object_id)
                        self.commands.extend(Controller.get_add_physics_object(model_name=coaster_model_name,
                                                                               position=TDWUtils.array_to_vector3(cup_position),
                                                                               rotation={"x": 0, "y": float(self.rng.randint(-25, 25)), "z": 0},
                                                                               object_id=object_id,
                                                                               library="models_core.json"))
                        coaster_record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(coaster_model_name)
                        y = cup_position[1] + coaster_record.bounds["top"]["y"]
                    else:
                        y = cup_position[1]
                    # Add a cup or wine glass.
                    if self.rng.random() > 0.5:
                        cup_category = "cup"
                    else:
                        cup_category = "wineglass"
                    cups = ProcGenObjects.MODEL_CATEGORIES[cup_category]
                    cup_model_name = cups[self.rng.randint(0, len(cups))]
                    # Add the cup.
                    object_id = Controller.get_unique_id()
                    child_object_ids.append(object_id)
                    self.commands.extend(Controller.get_add_physics_object(model_name=cup_model_name,
                                                                           object_id=object_id,
                                                                           position={"x": float(cup_position[0]),
                                                                                     "y": y,
                                                                                     "z": float(cup_position[2])},
                                                                           rotation={"x": 0,
                                                                                     "y": float(self.rng.uniform(0, 360)),
                                                                                     "z": 0},
                                                                           library="models_core.json"))
                plate_height = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(plate_model_name).bounds["top"]["y"]
                # Add food.
                if self.rng.random() < 0.66:
                    food_categories = ["apple", "banana", "chocolate", "orange", "sandwich"]
                    food_category: str = food_categories[self.rng.randint(0, len(food_categories))]
                    food = ProcGenObjects.MODEL_CATEGORIES[food_category]
                    food_model_name = food[self.rng.randint(0, len(food))]
                    food_position = [plate_position[0] + self.rng.uniform(-0.05, 0.05),
                                     plate_position[1] + plate_height,
                                     plate_position[2] + self.rng.uniform(-0.05, 0.05)]
                    object_id = Controller.get_unique_id()
                    child_object_ids.append(object_id)
                    self.commands.extend(Controller.get_add_physics_object(model_name=food_model_name,
                                                                           object_id=object_id,
                                                                           position=TDWUtils.array_to_vector3(food_position),
                                                                           rotation={"x": 0,
                                                                                     "y": rotation + float(self.rng.uniform(0, 360)),
                                                                                     "z": 0},
                                                                           library="models_core.json"))
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

    def _add_shelf(self, record: ModelRecord, position: Dict[str, float], face_away_from: float) -> None:
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
                                                               position=position,
                                                               kinematic=True))
        size = (ProcGenKitchen._SHELVES[record.name]["size"][0], ProcGenKitchen._SHELVES[record.name]["size"][1])
        # Add objects to each shelf.
        child_object_ids: List[int] = list()
        for y in ProcGenKitchen._SHELVES[record.name]["ys"]:
            object_top = {"x": position["x"], "y": y + position["y"], "z": position["z"]}
            cell_size, density = self._get_rectangular_arrangement_parameters(category="shelf")
            object_ids = self.add_rectangular_arrangement(size=size,
                                                          categories=ProcGenKitchen._ON_SHELF,
                                                          center=object_top,
                                                          cell_size=cell_size,
                                                          density=density)
            child_object_ids.extend(object_ids)
        # Rotate everything.
        self.add_rotation_commands(parent_object_id=root_object_id,
                                   child_object_ids=child_object_ids,
                                   rotation=rotation)

    def _add_kitchen_counter(self, record: ModelRecord, position: Dict[str, float],
                             face_away_from: CardinalDirection = None) -> None:
        """
        Procedurally generate a kitchen counter with objects on it.
        Sometimes, a kitchen counter will have a microwave, which can have objects on top of it.
        There will never be more than 1 microwave in the scene.

        :param record: The model record.
        :param position: The position of the root object as either a numpy array or a dictionary.
        :param face_away_from: The direction that the object is facing away from. For example, if this is `north`, then the object is looking southwards.

        :return: The model record of the root object. If no models were added to the scene, this is None.
        """

        if face_away_from == CardinalDirection.north:
            rotation: int = 0
        elif face_away_from == CardinalDirection.south:
            rotation = 360
        elif face_away_from == CardinalDirection.west:
            rotation = 90
        elif face_away_from == CardinalDirection.east:
            rotation = 270
        else:
            raise Exception(face_away_from)
        # Add objects on the kitchen counter.
        if self.rng.random() < 0.5 or "microwave" in self._used_unique_categories:
            return self.add_object_with_other_objects_on_top(record=record, position=position, rotation=rotation,
                                                             category="kitchen_counter")
        # Add a microwave on the kitchen counter.
        else:
            root_object_id = Controller.get_unique_id()
            self.commands.extend(Controller.get_add_physics_object(model_name=record.name,
                                                                   object_id=root_object_id,
                                                                   position=position,
                                                                   rotation={"x": 0, "y": rotation, "z": 0},
                                                                   library="models_core.json",
                                                                   kinematic=True))
            # Get the top position of the kitchen counter.
            object_top = {"x": position["x"],
                          "y": record.bounds["top"]["y"] + position["y"],
                          "z": position["z"]}
            # Add a microwave and add objects on top of the microwave.
            self.add_object_with_other_objects_on_top(record=record, position=object_top, rotation=rotation,
                                                      category="microwave")

    def _add_kitchen_counter_top_at_position(self, position: Dict[str, float]) -> None:
        """
        Add a floating (kinematic) kitchen counter top to the scene.

        :param position: The position of the kitchen counter top. The y coordinate will be adjusted.
        """

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
                               "scale_factor": {"x": ProcGenKitchen._KITCHEN_COUNTER_TOP_SIZE,
                                                "y": 0.0371,
                                                "z": ProcGenKitchen._KITCHEN_COUNTER_TOP_SIZE}},
                              {"$type": "set_kinematic_state",
                               "id": object_id,
                               "kinematic": True}])

    def _add_kitchen_counter_top_at_corner(self, corner: OrdinalDirection) -> Dict[str, float]:
        """
        Add a floating kitchen counter top in the corner of the room.

        :param corner: The corner.

        :return: The position of the kitchen counter top.
        """

        room = self.scene_bounds.rooms[self._region]
        if corner == OrdinalDirection.northwest:
            position = {"x": room.x_min + ProcGenObjects._WALL_DEPTH + ProcGenKitchen._KITCHEN_COUNTER_TOP_SIZE / 2,
                        "y": 0,
                        "z": room.z_max - ProcGenObjects._WALL_DEPTH - ProcGenKitchen._KITCHEN_COUNTER_TOP_SIZE / 2}
        elif corner == OrdinalDirection.northeast:
            position = {"x": room.x_max - ProcGenObjects._WALL_DEPTH - ProcGenKitchen._KITCHEN_COUNTER_TOP_SIZE / 2,
                        "y": 0,
                        "z": room.z_max - ProcGenObjects._WALL_DEPTH - ProcGenKitchen._KITCHEN_COUNTER_TOP_SIZE / 2}
        elif corner == OrdinalDirection.southwest:
            position = {"x": room.x_min + ProcGenObjects._WALL_DEPTH + ProcGenKitchen._KITCHEN_COUNTER_TOP_SIZE / 2,
                        "y": 0,
                        "z": room.z_min + ProcGenObjects._WALL_DEPTH + ProcGenKitchen._KITCHEN_COUNTER_TOP_SIZE / 2}
        elif corner == OrdinalDirection.southeast:
            position = {"x": room.x_max - ProcGenObjects._WALL_DEPTH - ProcGenKitchen._KITCHEN_COUNTER_TOP_SIZE / 2,
                        "y": 0,
                        "z": room.z_min + ProcGenObjects._WALL_DEPTH + ProcGenKitchen._KITCHEN_COUNTER_TOP_SIZE / 2}
        else:
            raise Exception(corner)
        self._add_kitchen_counter_top_at_position(position=position)
        return position

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

    def _add_lateral_arrangement(self, start_position: Dict[str, float], categories: List[str], face_away_from: CardinalDirection, length: float):
        def __get_long_extent() -> float:
            record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(model_name)
            warg = 1
        distance = 0
        # Choose a random starting object.
        model_names = ProcGenObjects.MODEL_CATEGORIES[categories[0]][:]
        self.rng.shuffle(model_names)
        first_model_name = ""
        got_model_name = False
        for model_name in model_names:

    @staticmethod
    def _mirror_x(positions: List[Dict[str]]) -> List[dict]:
        """
        :param positions: A list of positions.

        :return: A list of positions with the x coordinate sign flipped.
        """

        return [{"x": -p["x"], "y": p["y"], "z": p["z"]} for p in positions]

    @staticmethod
    def _mirror_z(positions: List[Dict[str]]) -> List[dict]:
        """
        :param positions: A list of positions.

        :return: A list of positions with the z coordinate sign flipped.
        """

        return [{"x": p["x"], "y": p["y"], "z": -p["z"]} for p in positions]
