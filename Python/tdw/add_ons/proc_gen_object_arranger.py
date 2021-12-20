from json import loads
from pathlib import Path
from pkg_resources import resource_filename
from typing import Tuple, List, Union, Dict, Optional
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller
from tdw.librarian import ModelLibrarian, ModelRecord
from tdw.add_ons.proc_gen_object_arrangement.spatial_relation import SpatialRelation, SPATIAL_RELATIONS
from tdw.add_ons.proc_gen_object_arrangement.arrangement_result import ArrangementResult
from tdw.scene_data.region_bounds import RegionBounds
from tdw.scene_data.scene_bounds import SceneBounds
from tdw.add_ons.add_on import AddOn


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


class ProcGenObjectArranger(AddOn):
    """
    Procedurally arrange objects using spatial relations and categories.
    For example, certain object categories can be *on top of* other object categories.

    Note that proc-gen object categories overlap with `record.wcategory` but are not the same.
    Note also that not all objects in a wcategory suitable for proc-gen and so aren't used by this add-on.
    To determine all models in a proc-gen category and the corresponding wcategory:

    ```python
    from tdw.add_ons.proc_gen_object_arranger import ProcGenObjectArranger

    for proc_gen_category in ProcGenObjectArranger.PROC_GEN_CATEGORY_TO_WCATEGORY:
        wcategory = ProcGenObjectArranger.PROC_GEN_CATEGORY_TO_WCATEGORY[proc_gen_category]
        print(f"Proc-gen category: {proc_gen_category}", f"wcategory: {wcategory}")
        for model_name in ProcGenObjectArranger.MODEL_CATEGORIES[proc_gen_category]:
            print(f"\t{model_name}")
    ```
    """

    # Cache the model librarian.
    if "models_core.json" not in Controller.MODEL_LIBRARIANS:
        Controller.MODEL_LIBRARIANS["models_core.json"] = ModelLibrarian("models_core.json")
    """:class_var
    The names of models suitable for proc-gen. Key = The category. Value = A list of model names.
    """
    MODEL_CATEGORIES: Dict[str, List[str]] = loads(Path(resource_filename(__name__, "proc_gen_object_arrangement/models.json")).read_text())
    """:class_var
    Objects in these categories will be kinematic.
    """
    KINEMATIC_CATEGORIES: List[str] = Path(resource_filename(__name__, "proc_gen_object_arrangement/kinematic_categories.txt")).read_text().split("\n")
    """:class_var
    Data for shelves. Key = model name. Value = Dictionary: "size" (a 2-element list), "ys" (list of shelf y's).
    """
    SHELVES: Dict[str, dict] = loads(Path(resource_filename(__name__, "proc_gen_object_arrangement/shelves.json")).read_text())
    """:class_var
    Parameters for rectangular arrangements. Key = Category. Value = Dictionary (`"cell_size"`, `"density"`).
    """
    RECTANGULAR_ARRANGEMENTS: Dict[str, dict] = loads(Path(resource_filename(__name__, "proc_gen_object_arrangement/rectangular_arrangements.json")).read_text())
    """:class_var
    A mapping of proc-gen categories to record wcategories.
    """
    PROC_GEN_CATEGORY_TO_WCATEGORY: Dict[str, str] = loads(Path(resource_filename(__name__, "proc_gen_object_arrangement/procgen_category_to_wcategory.json")).read_text())

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
        self._arrangement_results: List[ArrangementResult] = list()

    def get_initialization_commands(self) -> List[dict]:
        return [{"$type": "send_scene_regions"}]

    def on_send(self, resp: List[bytes]) -> None:
        if self.scene_bounds is None:
            self.scene_bounds = SceneBounds(resp=resp)

    def reset(self) -> None:
        """
        :return: Call this whenever you reset the scene or load a new scene.
        """

        self.initialized = False
        self.scene_bounds = None

    def get_arrangement(self, category: str, position: Union[np.array, Dict[str, float]],
                        rotation: float, region: int = 0) -> None:
        """
        Procedurally generate an arrangement of objects.

        :param category: The category of the "root" object.
        :param position: The position of the root object as either a numpy array or a dictionary.
        :param rotation: The root object's rotation in degrees around the y axis; all other objects will be likewise rotated.
        :param region: The index of the region in `self.scene_bounds`.
        """

        assert category in ProcGenObjectArranger.MODEL_CATEGORIES, f"Invalid category: {category}"
        region_bounds = self.scene_bounds.rooms[region]
        # Get the root object position as a dictionary.
        if isinstance(position, dict):
            object_position = position
        elif isinstance(position, np.ndarray) or isinstance(position, list):
            object_position = TDWUtils.array_to_vector3(position)
        else:
            raise Exception(f"Invalid position argument: {position}")
        # Get the possible root objects.
        record = self._get_model_that_fits_in_region(model_names=ProcGenObjectArranger.MODEL_CATEGORIES[category][:],
                                                     object_position=object_position,
                                                     region_bounds=region_bounds)
        # There are no root objects that fit.
        if record is None:
            return
        result = self._get_arrangement_from_root_model(record=record,
                                                       category=category,
                                                       root_object_position=object_position,
                                                       rotation=rotation,
                                                       region_bounds=region_bounds,
                                                       commands=[],
                                                       is_root=True)
        if result.success:
            self._arrangement_results.append(result)
            # Append the commands.
            self.commands.extend(result.commands)

    def _get_arrangement_from_root_model(self, record: ModelRecord, category: str,
                                         root_object_position: Dict[str, float], rotation: float,
                                         region_bounds: RegionBounds, commands: List[dict],
                                         is_root: bool) -> ArrangementResult:
        """
        Procedurally generate an arrangement of objects from a root object.

        :param record: The record of the root object.
        :param category: The category of the "root" object.
        :param root_object_position: The position of the root object as a dictionary.
        :param rotation: The root object's rotation in degrees around the y axis; all other objects will be likewise rotated.
        :param region_bounds: The bounds of the region.
        :param commands: The list of commands so far.
        :param is_root: If True, this is the root object of the whole tree.

        :return: An [`ArrangementResult`](arrangement_result.md).
        """

        root_object_id = Controller.get_unique_id()
        commands.extend(Controller.get_add_physics_object(model_name=record.name,
                                                          position=root_object_position,
                                                          library="models_core.json",
                                                          object_id=root_object_id,
                                                          kinematic=record.name in ProcGenObjectArranger.KINEMATIC_CATEGORIES))
        # Get the size of the model.
        model_size = ProcGenObjectArranger._get_size(record=record)
        categories: List[str] = [category]
        # Add objects base on spatial relationship.
        for spatial_relation in SPATIAL_RELATIONS:
            if category not in SPATIAL_RELATIONS[spatial_relation]:
                continue
            # Put objects on top of the root object.
            if spatial_relation == SpatialRelation.on_top_of:
                # Gert the top position of the object.
                object_top = {"x": root_object_position["x"],
                              "y": record.bounds["top"]["y"] + root_object_position["y"],
                              "z": root_object_position["z"]}
                cell_size, density = self._get_rectangular_arrangement_parameters(category=category)
                surface_size = (model_size[0] * 0.8, model_size[1] * 0.8)
                object_commands, object_categories = self._get_rectangular_arrangement(size=surface_size,
                                                                                       categories=SPATIAL_RELATIONS[
                                                                                           spatial_relation][category],
                                                                                       center=object_top,
                                                                                       cell_size=cell_size,
                                                                                       density=density)
                categories.extend(object_categories)
                commands.extend(object_commands)
            # Put objects on top of the shelves of the root object.
            elif spatial_relation == SpatialRelation.on_shelf:
                size = (ProcGenObjectArranger.SHELVES[record.name]["size"][0],
                        ProcGenObjectArranger.SHELVES[record.name]["size"][1])
                for y in ProcGenObjectArranger.SHELVES[record.name]["ys"]:
                    object_top = {"x": root_object_position["x"],
                                  "y": y + root_object_position["y"],
                                  "z": root_object_position["z"]}
                    cell_size, density = self._get_rectangular_arrangement_parameters(category=category)
                    object_commands, object_categories = self._get_rectangular_arrangement(size=size,
                                                                                           categories=SPATIAL_RELATIONS[
                                                                                               spatial_relation][
                                                                                               category],
                                                                                           center=object_top,
                                                                                           cell_size=cell_size,
                                                                                           density=density)
                    categories.extend(object_categories)
                    commands.extend(object_commands)
            # Add an arrangement to the left and right of this object, if possible.
            elif spatial_relation == SpatialRelation.left_or_right_of and is_root:
                for is_left in [True, False]:
                    arrangement_result = self._get_left_or_right_arrangement(root_object_position=root_object_position,
                                                                             root_object_record=record,
                                                                             root_object_category=category,
                                                                             region_bounds=region_bounds,
                                                                             is_left=is_left,
                                                                             rotation=rotation,
                                                                             commands=commands)
                    # Append the result.
                    if arrangement_result.success:
                        commands.extend(arrangement_result.commands)
                        categories.extend(arrangement_result.categories)
        # Get a list of object IDs.
        object_ids: List[int] = list()
        kinematic_object_ids: List[int] = list()
        for command in commands:
            if command["$type"] == "add_object":
                object_ids.append(command["id"])
            elif command["$type"] == "set_kinematic_state" and command["is_kinematic"]:
                kinematic_object_ids.append(command["id"])
        # Rotate the root object.
        if is_root:
            parent_commands = []
            for command in commands:
                if command["$type"] == "add_object" and command["id"] != root_object_id:
                    parent_commands.append({"$type": "parent_object_to_object",
                                            "id": command["id"],
                                            "parent_id": root_object_id})
            commands.extend(parent_commands)
            commands.append({"$type": "rotate_object_by",
                             "angle": rotation,
                             "id": root_object_id,
                             "axis": "yaw",
                             "is_world": True,
                             "use_centroid": False})
            # Unparent everything.
            unparent_commands = []
            for command in commands:
                if command["$type"] == "add_object" and command["id"] != root_object_id:
                    unparent_commands.append({"$type": "unparent_object",
                                              "id": command["id"]})
            commands.extend(unparent_commands)
        # Return a description of the result.
        return ArrangementResult(success=True, object_ids=object_ids, kinematic_object_ids=kinematic_object_ids,
                                 categories=list(set(categories)), commands=commands)

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

        def __get_circle_mask(circle_x: int, circle_y: int, radius: float) -> np.array:
            """
            Source: https://www.semicolonworld.com/question/44279/how-to-apply-a-disc-shaped-mask-to-a-numpy-array

            :param circle_x: The x coordinate of the circle.
            :param circle_y: The y coordinate of the circle.
            :param radius: The radius of the circle in indices.

            :return: A boolean array. True = The element is within the circle.
            """

            nx, ny = occupancy_map.shape
            oy, ox = np.ogrid[-circle_x:nx - circle_x, -circle_y:ny - circle_y]
            return ox * ox + oy * oy <= radius * radius

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
        bad_categories = [c for c in categories if c not in ProcGenObjectArranger.MODEL_CATEGORIES]
        if len(bad_categories) > 0:
            print(f"WARNING! Invalid model categories: {bad_categories}")
        # Get the semi-minor axis of the rectangle's size.
        semi_minor_axis = (size[0] if size[0] < size[1] else size[1]) - (cell_size * 2)
        # Get valid objects.
        model_sizes: Dict[str, float] = dict()
        model_cell_sizes: List[int] = list()
        models_and_categories: Dict[str, str] = dict()
        for category in categories:
            if category not in ProcGenObjectArranger.MODEL_CATEGORIES:
                continue
            # Get objects small enough to fit within the rectangle.
            for model_name in ProcGenObjectArranger.MODEL_CATEGORIES[category]:
                record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(model_name)
                model_size = ProcGenObjectArranger._get_size(record=record)
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
                    circle_mask = __get_circle_mask(circle_x=ix, circle_y=iz, radius=mcs)
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
            if model_category in ProcGenObjectArranger.KINEMATIC_CATEGORIES:
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
            occupancy_map[__get_circle_mask(circle_x=ix, circle_y=iz, radius=sma) == True] = True
        return commands, list(set(model_categories))

    def _get_left_or_right_arrangement(self, root_object_position: Dict[str, float], root_object_record: ModelRecord,
                                       root_object_category: str, region_bounds: RegionBounds,
                                       is_left: bool, rotation: float, commands: List[dict]) -> ArrangementResult:
        """
        Add an arrangement to the left or right of a root object.

        :param root_object_position: The position of the root object.
        :param root_object_record: The root object record.
        :param root_object_category: The root object category.
        :param region_bounds: The bounds of the region (room).
        :param is_left: If True, add an arrangement to the left of the root object. If False, add an object to the right.
        :param rotation: The rotation of the root object and the objects to its left and right.
        :param commands: The commands generated so far.

        :return: An `ArrangementResult`.
        """

        # Get the bounds positions of all objects so far.
        object_bounds: List[_ObjectBounds] = list()
        for command in commands:
            if command["$type"] == "add_object":
                r = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(command["name"])
                object_bounds.append(_ObjectBounds(record=r, root_object_position=root_object_position))
        # Get an object that fits in the room and doesn't overlap with any existing models.
        model_categories: List[str] = SPATIAL_RELATIONS[SpatialRelation.left_or_right_of][root_object_category][:]
        self.rng.shuffle(model_categories)
        got_model_name = False
        record = Controller.MODEL_LIBRARIANS["models_core.json"].records[0]
        position = {"x": 0, "y": 0, "z": 0}
        for model_category in model_categories:
            if got_model_name:
                break
            model_names = ProcGenObjectArranger.MODEL_CATEGORIES[model_category][:]
            self.rng.shuffle(model_names)
            for model_name in model_names:
                record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(model_name)
                # Get the position of the object.
                if is_left:
                    x = root_object_position["x"] + root_object_record.bounds["left"]["x"] + record.bounds["left"]["x"]
                else:
                    x = root_object_position["x"] + root_object_record.bounds["right"]["x"] + record.bounds["right"]["x"]
                position = {"x": x, "y": root_object_position["y"], "z": root_object_position["z"]}
                # Don't use this object if it overlaps with any others.
                in_bounds = False
                for ob in object_bounds:
                    if ob.is_inside(x=position["x"], z=position["z"]):
                        in_bounds = True
                        break
                if in_bounds:
                    continue
                # Use this object if it fits within the scene region.
                if ProcGenObjectArranger._model_fits_in_region(record=record, region_bounds=region_bounds, position=position):
                    got_model_name = True
                    break
        # No object fits here.
        if not got_model_name:
            return ArrangementResult(success=False, object_ids=[], kinematic_object_ids=[], categories=[], commands=[])
        return self._get_arrangement_from_root_model(record=record,
                                                     root_object_position=position,
                                                     category=root_object_category,
                                                     rotation=rotation,
                                                     region_bounds=region_bounds,
                                                     commands=[],
                                                     is_root=False)

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

        if category not in ProcGenObjectArranger.RECTANGULAR_ARRANGEMENTS:
            return 0.05, 0.4
        return ProcGenObjectArranger.RECTANGULAR_ARRANGEMENTS[category]["cell_size"], ProcGenObjectArranger.RECTANGULAR_ARRANGEMENTS[category]["density"]

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

    def _get_model_that_fits_in_region(self, model_names: List[str], object_position: Dict[str, float],
                                       region_bounds: RegionBounds) -> Optional[ModelRecord]:
        self.rng.shuffle(model_names)
        # Get the first object, if any, that fits in the region bounds.
        got_model_name = False
        record = Controller.MODEL_LIBRARIANS["models_core.json"].records[0]
        for mn in model_names:
            record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(mn)
            if ProcGenObjectArranger._model_fits_in_region(record=record, position=object_position,
                                                           region_bounds=region_bounds):
                got_model_name = True
                break
        if not got_model_name:
            return None
        else:
            return record
