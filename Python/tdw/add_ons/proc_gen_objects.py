from enum import Enum
from json import loads
from pathlib import Path
from pkg_resources import resource_filename
from typing import Tuple, List, Union, Dict, Optional
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller
from tdw.librarian import ModelLibrarian, ModelRecord
from tdw.add_ons.proc_gen_objects.room_type import RoomType, ROOM_TYPE_LATERAL_SPATIAL_RELATIONS
from tdw.scene_data.region_bounds import RegionBounds
from tdw.scene_data.scene_bounds import SceneBounds
from tdw.add_ons.add_on import AddOn
from tdw.cardinal_direction import CardinalDirection


class _VerticalSpatialRelation(Enum):
    """
    Enum values to define vertical spatial relations.
    """

    on_top_of = 1
    on_shelf = 2


class _ObjectBounds:
    """
    Object bound positions based on cached object bounds and the position of the root object, assuming no rotation.
    """
    def __init__(self, record: ModelRecord, root_object_position: Dict[str, float]):
        """
        :param record: The model record.
        :param root_object_position: The position of the root object.
        """

        self.x_min: float = root_object_position["x"] + record.bounds["left"]["x"]
        self.x_max: float = root_object_position["x"] + record.bounds["right"]["x"]
        self.z_min: float = root_object_position["z"] + record.bounds["front"]["z"]
        self.z_max: float = root_object_position["z"] + record.bounds["back"]["z"]

    def is_inside(self, x: float, z: float) -> bool:
        """
        :param x: The x coordinate.
        :param z: The z coordinate.

        :return: True if position (x, z) is within the bounds of this object.
        """

        return self.x_min <= x <= self.x_max and self.z_min <= z <= self.z_max


class ProcGenObjects(AddOn):
    """
    Procedurally arrange objects using spatial relations and categories.
    For example, certain object categories can be *on top of* other object categories.

    Note that proc-gen object categories overlap with `record.wcategory` but are not the same.
    Note also that not all objects in a wcategory suitable for proc-gen and so aren't used by this add-on.
    To determine all models in a proc-gen category and the corresponding wcategory:

    ```python
    from tdw.add_ons.proc_gen_objects import ProcGenObjects

    for proc_gen_category in ProcGenObjects.PROC_GEN_CATEGORY_TO_WCATEGORY:
        wcategory = ProcGenObjects.PROC_GEN_CATEGORY_TO_WCATEGORY[proc_gen_category]
        print(f"Proc-gen category: {proc_gen_category}", f"wcategory: {wcategory}")
        for model_name in ProcGenObjects.MODEL_CATEGORIES[proc_gen_category]:
            print(f"\t{model_name}")
    ```
    """

    # Cache the model librarian.
    if "models_core.json" not in Controller.MODEL_LIBRARIANS:
        Controller.MODEL_LIBRARIANS["models_core.json"] = ModelLibrarian("models_core.json")
    """:class_var
    The names of models suitable for proc-gen. Key = The category. Value = A list of model names.
    """
    MODEL_CATEGORIES: Dict[str, List[str]] = loads(Path(resource_filename(__name__, "proc_gen_objects/models.json")).read_text())
    """:class_var
    Objects in these categories will be kinematic.
    """
    KINEMATIC_CATEGORIES: List[str] = Path(resource_filename(__name__, "proc_gen_objects/kinematic_categories.txt")).read_text().split("\n")
    """:class_var
    Data for shelves. Key = model name. Value = Dictionary: "size" (a 2-element list), "ys" (list of shelf y's).
    """
    SHELVES: Dict[str, dict] = loads(Path(resource_filename(__name__, "proc_gen_objects/shelves.json")).read_text())
    """:class_var
    Parameters for rectangular arrangements. Key = Category. Value = Dictionary (`"cell_size"`, `"density"`).
    """
    RECTANGULAR_ARRANGEMENTS: Dict[str, dict] = loads(Path(resource_filename(__name__, "proc_gen_objects/rectangular_arrangements.json")).read_text())
    """:class_var
    A mapping of proc-gen categories to record wcategories.
    """
    PROC_GEN_CATEGORY_TO_WCATEGORY: Dict[str, str] = loads(Path(resource_filename(__name__, "proc_gen_objects/procgen_category_to_wcategory.json")).read_text())
    # Categories that should only appear once in a scene.
    _UNIQUE_CATEGORIES: List[str] = Path(resource_filename(__name__, "proc_gen_objects/unique_categories.txt")).read_text().split("\n")
    _WALL_DEPTH: float = 0.28

    def __init__(self, random_seed: int = None):
        """
        :param random_seed: The random seed. If None, a random seed is randomly selected.
        """

        super().__init__()
        if random_seed is None:
            """:field
            The random number generator.
            """
            self.rng: np.random.RandomState = np.random.RandomState()
        else:
            self.rng = np.random.RandomState(random_seed)
        """:field
        The [scene bounds](../scene_data/SceneBounds.md). This is set on the second `communicate()` call.
        """
        self.scene_bounds: Optional[SceneBounds] = None
        # Get the vertical spatial relations.
        vertical_spatial_relations_data = loads(Path(resource_filename(__name__, "vertical_spatial_relations.json")).read_text())
        self._vertical_spatial_relations: Dict[_VerticalSpatialRelation, Dict[str, List[str]]] = dict()
        for r in vertical_spatial_relations_data:
            self._vertical_spatial_relations[_VerticalSpatialRelation[r]] = dict()
            for c in vertical_spatial_relations_data[r]:
                self._vertical_spatial_relations[_VerticalSpatialRelation[r]][c] = vertical_spatial_relations_data[r][c]
        self._used_unique_categories: List[str] = list()

    def get_initialization_commands(self) -> List[dict]:
        self._used_unique_categories.clear()
        self.scene_bounds = None
        return [{"$type": "send_scene_regions"}]

    def on_send(self, resp: List[bytes]) -> None:
        if self.scene_bounds is None:
            self.scene_bounds = SceneBounds(resp=resp)

    def add_shelf(self, position: Union[np.array, Dict[str, float]], rotation: float,
                  region: int = 0) -> Optional[ModelRecord]:
        """
        Procedurally generate a shelf with objects on each shelf.

        :param position: The position of the root object as either a numpy array or a dictionary.
        :param rotation: The root object's rotation in degrees around the y axis; all other objects will be likewise rotated.
        :param region: The index of the region in `self.scene_bounds`.

        :return: The model record of the root object. If no models were added to the scene, this is None.
        """

        record, root_object_id, position = self._get_root_object(category="shelf", position=position, region=region)
        if record is None:
            return None
        size = (ProcGenObjects.SHELVES[record.name]["size"][0], ProcGenObjects.SHELVES[record.name]["size"][1])
        # Add objects to each shelf.
        on_shelf_categories = self._vertical_spatial_relations[_VerticalSpatialRelation.on_shelf]["shelf"]
        for y in ProcGenObjects.SHELVES[record.name]["ys"]:
            object_top = {"x": position["x"], "y": y + position["y"], "z": position["z"]}
            cell_size, density = self._get_rectangular_arrangement_parameters(category="shelf")
            object_commands, object_categories = self._get_rectangular_arrangement(size=size,
                                                                                   categories=on_shelf_categories,
                                                                                   center=object_top,
                                                                                   cell_size=cell_size,
                                                                                   density=density)
            self.commands.extend(object_commands)
        # Rotate everything.
        self._add_rotation_commands(root_object_id=root_object_id, rotation=rotation)
        return record

    def add_kitchen_counter(self, position: Union[np.array, Dict[str, float]], rotation: float,
                            region: int = 0) -> Optional[ModelRecord]:
        """
        Procedurally generate a kitchen counter with objects on it.
        Sometimes, a kitchen counter will have a microwave, which can have objects on top of it.
        There will never be more than 1 microwave in the scene.

        :param position: The position of the root object as either a numpy array or a dictionary.
        :param rotation: The root object's rotation in degrees around the y axis; all other objects will be likewise rotated.
        :param region: The index of the region in `self.scene_bounds`.

        :return: The model record of the root object. If no models were added to the scene, this is None.
        """

        # Add objects on the kitchen counter.
        if self.rng.random() < 0.5 or "microwave" not in self._used_unique_categories:
            return self._get_objects_on_top_of(position=position, rotation=rotation, region=region,
                                               category="kitchen_counter")
        # Add a microwave on the kitchen counter.
        else:
            record, root_object_id, object_position = self._get_root_object(category="kitchen_counter",
                                                                            position=position,
                                                                            region=region)
            if record is None:
                return None
            # Rotate the kitchen counter.
            self._add_rotation_commands(root_object_id=root_object_id, rotation=rotation)
            # Get the top position of the kitchen counter.
            object_top = {"x": object_position["x"],
                          "y": record.bounds["top"]["y"] + object_position["y"],
                          "z": object_position["z"]}
            # Add a microwave and add objects on top of the microwave.
            self._get_objects_on_top_of(position=object_top, rotation=rotation, region=region, category="microwave",
                                        parent=record)
            return record

    def _get_root_object(self, category: str, position: Union[np.array, Dict[str, float]], region: int = 0,
                         parent: ModelRecord = None) -> Tuple[Optional[ModelRecord], int, Dict[str, float]]:
        """
        Try to add a root object to the scene.

        :param category: The category of the root object.
        :param position: The position of the root object as either a numpy array or a dictionary.
        :param region: The index of the region in `self.scene_bounds`.
        :param parent: The record of the parent object.

        :return: Tuple: A model record (None if the object wasn't added), the object ID (-1 if the object wasn't added), the object position as a dictionary.
        """

        region_bounds = self.scene_bounds.rooms[region]
        # Get the root object position as a dictionary.
        if isinstance(position, dict):
            object_position = position
        elif isinstance(position, np.ndarray) or isinstance(position, list):
            object_position = TDWUtils.array_to_vector3(position)
        else:
            raise Exception(f"Invalid position argument: {position}")
        # Get the possible root objects.
        record = self._get_model_that_fits_in_region(model_names=ProcGenObjects.MODEL_CATEGORIES[category][:],
                                                     object_position=object_position,
                                                     region_bounds=region_bounds,
                                                     parent=parent)
        if record is None:
            return None, -1, object_position
        # Record that this category has been used.
        if category in ProcGenObjects._UNIQUE_CATEGORIES:
            self._used_unique_categories.append(category)
        root_object_id = Controller.get_unique_id()
        self.commands.extend(Controller.get_add_physics_object(model_name=record.name,
                                                               position=object_position,
                                                               library="models_core.json",
                                                               object_id=root_object_id,
                                                               kinematic=category in ProcGenObjects.KINEMATIC_CATEGORIES))
        return record, root_object_id, object_position

    def _get_objects_on_top_of(self, category: str, position: Union[np.array, Dict[str, float]], rotation: float,
                               region: int = 0, parent: ModelRecord = None) -> Optional[ModelRecord]:
        """
        Add a root object and add objects on  top of it.

        :param category: The category of the root object.
        :param position: The position of the root object.
        :param rotation: The rotation of the root object.
        :param region: The index of the region in `self.scene_bounds`.
        :param parent: The record of the parent object. Can be None.

        :return: A model record if anything was added to the scene.
        """

        record, root_object_id, object_position = self._get_root_object(category=category, position=position,
                                                                        region=region, parent=parent)
        if record is None:
            return None
        model_size = self._get_size(record=record)
        # Get the top position of the object.
        object_top = {"x": object_position["x"],
                      "y": record.bounds["top"]["y"] + object_position["y"],
                      "z": object_position["z"]}
        # Get the dimensions of the object's occupancy map.
        cell_size, density = self._get_rectangular_arrangement_parameters(category=category)
        surface_size = (model_size[0] * 0.8, model_size[1] * 0.8)
        # Add objects on top of the root object.
        object_commands, object_categories = self._get_rectangular_arrangement(size=surface_size,
                                                                               categories=self._vertical_spatial_relations[_VerticalSpatialRelation.on_top_of][category],
                                                                               center=object_top,
                                                                               cell_size=cell_size,
                                                                               density=density)
        self.commands.extend(object_commands)
        # Rotate everything.
        self._add_rotation_commands(root_object_id=root_object_id, rotation=rotation)
        return record

    def get_lateral_arrangement(self, wall: CardinalDirection, room_type: RoomType = RoomType.kitchen, room_id: int = 0) -> None:
        room = self.scene_bounds.rooms[room_id]
        if wall == CardinalDirection.north:
            position = {"x": room.x_min + ProcGenObjects._WALL_DEPTH + 0.4,
                        "y": 0,
                        "z": room.z_max - ProcGenObjects._WALL_DEPTH}
            direction = (1, 0)
            rotation: int = 0
            offset_direction = -1
            fixed_coordinate = position["z"]
        elif wall == CardinalDirection.south:
            position = {"x": room.x_min + ProcGenObjects._WALL_DEPTH + 0.4,
                        "y": 0,
                        "z": room.z_min + ProcGenObjects._WALL_DEPTH}
            direction = (1, 0)
            rotation = 180
            offset_direction = 1
            fixed_coordinate = position["z"]
        elif wall == CardinalDirection.west:
            position = {"x": room.x_max - ProcGenObjects._WALL_DEPTH,
                        "y": 0,
                        "z": room.z_min + ProcGenObjects._WALL_DEPTH + 0.4}
            direction = (0, 1)
            rotation = 90
            offset_direction = -1
            fixed_coordinate = position["x"]
        elif wall == CardinalDirection.east:
            position = {"x": room.x_min + ProcGenObjects._WALL_DEPTH,
                        "y": 0,
                        "z": room.z_min + ProcGenObjects._WALL_DEPTH + 0.4}
            direction = (0, 1)
            rotation = 270
            offset_direction = 1
            fixed_coordinate = position["x"]
        else:
            raise Exception(wall)
        done = False
        used_categories: List[str] = list()
        object_position = {"x": 0, "y": 0, "z": 0}
        while not done:
            # Get the name of a model.
            categories = ROOM_TYPE_LATERAL_SPATIAL_RELATIONS[room_type][:]
            categories = [c for c in categories if c not in used_categories]
            self.rng.shuffle(categories)
            got_model = False
            model_name = ""
            category = ""
            for c in categories:
                model_names = ProcGenObjects.MODEL_CATEGORIES[c][:]
                self.rng.shuffle(model_names)
                # Try to find a model that fits.
                got_model = False
                for m in model_names:
                    # Get the record.
                    record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(m)
                    # Get the size.
                    model_size = self._get_size(record=record)
                    # Get the position.
                    if direction[0] != 0:
                        p_x = position["x"] + model_size[1] * 0.5 * direction[0]
                        p_z = position["z"] + model_size[0] * 0.25 * offset_direction
                    elif direction[1] != 0:
                        p_x = position["x"] + model_size[0] * 0.25 * offset_direction
                        p_z = position["z"] + model_size[1] * 0.5 * direction[1]
                    else:
                        raise Exception(direction)
                    # If the model fits in the region, then we can add it.
                    object_position = {"x": p_x, "y": position["y"], "z": p_z}
                    if self._model_fits_in_region(record=record, position=object_position, region_bounds=room):
                        got_model = True
                        model_name = m
                        category = c
                        break
                if got_model:
                    break
            if not got_model:
                done = True
            else:
                # Add the object.
                rot = rotation - 180 if category != "kitchen_counter" else rotation
                record = self.get_vertical_arrangement_from_model(model_name=model_name,
                                                                  category=category,
                                                                  position=object_position,
                                                                  rotation=rot)
                # Remember that we used this category.
                if category != "kitchen_counter":
                    used_categories.append(category)
                # Move the position.
                position = {"x": object_position["x"], "y": object_position["y"], "z": object_position["z"]}
                size = self._get_size(record=record)
                # Additionally, move the position by this object's size.
                if direction[0] != 0:
                    position["x"] += size[0] * 0.5 * direction[0]
                    position["z"] = fixed_coordinate
                elif direction[1] != 0:
                    position["x"] = fixed_coordinate
                    position["z"] += size[0] * 0.5 * direction[1]

    def _get_rectangular_arrangement(self, size: Tuple[float, float], center: Union[np.array, Dict[str, float]],
                                     categories: List[str], density: float = 0.4,
                                     cell_size: float = 0.05) -> Tuple[List[dict], List[str]]:
        """
        Get a random arrangement of objects in a rectangular space.

        :param size: The size of the rectangle in worldspace coordinates.
        :param center: The position of the center of the rectangle.
        :param categories: Models will be randomly chosen from these categories.
        :param density: The probability of a "cell" in the arrangement being empty. Lower value = a higher density of small objects.
        :param cell_size: The size of each cell in the rectangle. This controls the minimum size of objects and the density of the arrangement.

        :return: Tuple: A list of commands to add the objects, the categories of objects.
        """

        # Get numpy array and dictionary representations of the center position.
        if isinstance(center, dict):
            center_dict = center
        else:
            center_dict = TDWUtils.array_to_vector3(center)
        if size[0] > size[1]:
            size = (size[1], size[0])
        # Get the x, z positions.
        xs: np.array = np.arange(cell_size, size[0] - cell_size, cell_size)
        zs: np.array = np.arange(cell_size, size[1] - cell_size, cell_size)
        # Get the occupancy map.
        occupancy_map: np.array = np.zeros(shape=(len(xs), len(zs)), dtype=bool)
        # Print a warning about bad categories.
        bad_categories = [c for c in categories if c not in ProcGenObjects.MODEL_CATEGORIES]
        if len(bad_categories) > 0:
            print(f"WARNING! Invalid model categories: {bad_categories}")
        # Get the semi-minor axis of the rectangle's size.
        semi_minor_axis = (size[0] if size[0] < size[1] else size[1]) - (cell_size * 2)
        # Get valid objects.
        model_sizes: Dict[str, float] = dict()
        model_cell_sizes: List[int] = list()
        models_and_categories: Dict[str, str] = dict()
        for category in categories:
            if category not in ProcGenObjects.MODEL_CATEGORIES:
                continue
            # Get objects small enough to fit within the rectangle.
            for model_name in ProcGenObjects.MODEL_CATEGORIES[category]:
                record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(model_name)
                model_size = ProcGenObjects._get_size(record=record)
                model_semi_major_axis = model_size[0] if model_size[0] > model_size[1] else model_size[1]
                if model_semi_major_axis < semi_minor_axis:
                    model_sizes[model_name] = model_semi_major_axis
                    model_cell_sizes.append(int(model_semi_major_axis / cell_size) + 1)
                    models_and_categories[model_name] = category
        commands: List[dict] = list()
        model_categories: List[str] = list()
        # Get all of the sizes in occupancy map space.
        model_cell_sizes = list(set(model_cell_sizes))
        model_cell_sizes.reverse()
        for ix, iz in np.ndindex(occupancy_map.shape):
            # Exclude edges.
            if ix == 0 or ix == occupancy_map.shape[0] - 1 or iz == 0 or iz == occupancy_map.shape[1]:
                continue
            # This position is already occupied. Sometimes, skip a position.
            if occupancy_map[ix][iz] or self.rng.random() < density:
                continue
            # Get the minimum object semi-major axis.
            sma = model_cell_sizes[0]
            for mcs in model_cell_sizes:
                # Stop if the the semi-major axis doesn't fit (it would fall off the edge).
                if ix - mcs < 0 or ix + mcs >= occupancy_map.shape[0] or iz - mcs < 0 or iz + mcs >= occupancy_map.shape[1]:
                    break
                else:
                    # Define the circle.
                    circle_mask = TDWUtils.get_circle_mask(shape=(occupancy_map.shape[0], occupancy_map.shape[1]),
                                                           row=ix, column=iz, radius=mcs)
                    # There is overlap. Stop here.
                    if np.count_nonzero((circle_mask == True) & (occupancy_map == True)) > 0:
                        break
                    else:
                        sma = mcs
            # Get all objects that fit.
            model_names = [m for m in model_sizes if int(model_sizes[m] / cell_size) <= sma]
            if len(model_names) == 0:
                continue
            # Choose a random model.
            model_name: str = model_names[self.rng.randint(0, len(model_names))]
            # Get the position. Perturb it slightly.
            x = (ix * cell_size) + self.rng.uniform(-cell_size * 0.025, cell_size * 0.025)
            z = (iz * cell_size) + self.rng.uniform(-cell_size * 0.025, cell_size * 0.025)
            # Offset from the center.
            x += center_dict["x"] - size[0] / 2 + cell_size
            z += center_dict["z"] - size[1] / 2 + cell_size
            # Cache the object ID.
            object_id = Controller.get_unique_id()
            # Set the rotation.
            model_category = models_and_categories[model_name]
            model_categories.append(model_category)
            if model_category in ProcGenObjects.KINEMATIC_CATEGORIES:
                object_rotation = 0
            else:
                object_rotation = self.rng.uniform(0, 360)
            # Add the object.
            commands.extend(Controller.get_add_physics_object(model_name=model_name,
                                                              position={"x": x, "y": center_dict["y"], "z": z},
                                                              rotation={"x": 0, "y": object_rotation, "z": 0},
                                                              object_id=object_id,
                                                              library="models_core.json"))
            # Record the position on the occupancy map.
            occupancy_map[TDWUtils.get_circle_mask(shape=(occupancy_map.shape[0], occupancy_map.shape[1]),
                                                   row=ix, column=iz, radius=sma) == True] = True
        return commands, list(set(model_categories))

    @staticmethod
    def _get_size(record: ModelRecord) -> Tuple[float, float]:
        """
        :param record: A model record.

        :return: Tuple: The left-right and front-back spans of the object bounds.
        """

        left_right = np.linalg.norm(TDWUtils.vector3_to_array(record.bounds["left"]) -
                                    TDWUtils.vector3_to_array(record.bounds["right"]))
        front_back = np.linalg.norm(TDWUtils.vector3_to_array(record.bounds["front"]) -
                                    TDWUtils.vector3_to_array(record.bounds["back"]))
        return left_right, front_back

    @staticmethod
    def _get_rectangular_arrangement_parameters(category: str) -> Tuple[float, float]:
        """
        :param category: The category

        :return: Tuple: The cell size and density.
        """

        if category not in ProcGenObjects.RECTANGULAR_ARRANGEMENTS:
            return 0.05, 0.4
        return ProcGenObjects.RECTANGULAR_ARRANGEMENTS[category]["cell_size"], ProcGenObjects.RECTANGULAR_ARRANGEMENTS[category]["density"]

    @staticmethod
    def _model_fits_in_region(record: ModelRecord, position: Dict[str, float], region_bounds: RegionBounds) -> bool:
        """
        :param record: The model record.
        :param position: The position of the object.
        :param region_bounds: The region (room) bounds.

        :return: True if the model fits in the region.
        """

        # Get the (x, z) positions of the bounds.
        for point in [[record.bounds["left"]["x"] + position["x"], record.bounds["left"]["z"] + position["z"]],
                      [record.bounds["right"]["x"] + position["x"], record.bounds["right"]["z"] + position["z"]],
                      [record.bounds["front"]["x"] + position["x"], record.bounds["front"]["z"] + position["z"]],
                      [record.bounds["back"]["x"] + position["x"], record.bounds["back"]["z"] + position["z"]],
                      [record.bounds["center"]["x"] + position["x"], record.bounds["center"]["z"] + position["z"]]]:
            if not region_bounds.is_inside(x=point[0], z=point[1]):
                return False
        return True

    def _get_model_that_fits_in_region(self, model_names: List[str],
                                       object_position: Dict[str, float],
                                       region_bounds: RegionBounds,
                                       parent: ModelRecord = None) -> Optional[ModelRecord]:
        self.rng.shuffle(model_names)
        # Get the first object, if any, that fits in the region bounds.
        got_model_name = False
        record = Controller.MODEL_LIBRARIANS["models_core.json"].records[0]
        for mn in model_names:
            record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(mn)
            if ProcGenObjects._model_fits_in_region(record=record, position=object_position,
                                                    region_bounds=region_bounds) and \
                    (parent is None or self._fits_inside(parent, record)):
                got_model_name = True
                break
        if not got_model_name:
            return None
        else:
            return record

    def _add_rotation_commands(self, root_object_id: int, rotation: float) -> None:
        """
        Add commands to parent the objects to the root object, rotate the root object, and unparent the objects.

        :param root_object_id: The ID of the root object.
        :param rotation: The rotation of the root object.
        """

        cmds = []
        # Parent all objects to the root object.
        for command in self.commands:
            if command["$type"] == "add_object" and command["id"] != root_object_id:
                cmds.append({"$type": "parent_object_to_object",
                             "id": command["id"],
                             "parent_id": root_object_id})
        # Rotate the root objects.
        cmds.append({"$type": "rotate_object_by",
                     "angle": rotation,
                     "id": root_object_id,
                     "axis": "yaw",
                     "is_world": True,
                     "use_centroid": False})
        # Unparent all of the objects from the root object.
        for command in self.commands:
            if command["$type"] == "add_object" and command["id"] != root_object_id:
                cmds.append({"$type": "unparent_object",
                             "id": command["id"]})
        self.commands.extend(cmds)

    @staticmethod
    def _fits_inside(parent: ModelRecord, child: ModelRecord) -> bool:
        """
        :param parent: The record of the parent object.
        :param child: The record of the child object.

        :return: True if the child object fits in the the parent object.
        """

        parent_extents = TDWUtils.get_bounds_extents(parent.bounds)
        child_extents = TDWUtils.get_bounds_extents(child.bounds)
        return parent_extents[0] > child_extents[0] and parent_extents[2] > child_extents[2]
