from enum import Enum
from json import loads
from pathlib import Path
from pkg_resources import resource_filename
from typing import Tuple, List, Union, Dict, Optional
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller
from tdw.librarian import ModelLibrarian, ModelRecord
from tdw.scene_data.scene_bounds import SceneBounds
from tdw.add_ons.add_on import AddOn


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
    Parameters for rectangular arrangements. Key = Category. Value = Dictionary (`"cell_size"`, `"density"`).
    """
    RECTANGULAR_ARRANGEMENTS: Dict[str, dict] = loads(Path(resource_filename(__name__, "proc_gen_objects/rectangular_arrangements.json")).read_text())
    """:class_var
    A mapping of proc-gen categories to record wcategories.
    """
    PROC_GEN_CATEGORY_TO_WCATEGORY: Dict[str, str] = loads(Path(resource_filename(__name__, "proc_gen_objects/procgen_category_to_wcategory.json")).read_text())
    _WALL_DEPTH: float = 0.28

    def __init__(self, random_seed: int = None, region: int = 0):
        """
        :param random_seed: The random seed. If None, a random seed is randomly selected.
        :param region: The ID of the scene region.
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
        vertical_spatial_relations_data = loads(Path(resource_filename(__name__, "proc_gen_objects/vertical_spatial_relations.json")).read_text())
        self._vertical_spatial_relations: Dict[_VerticalSpatialRelation, Dict[str, List[str]]] = dict()
        for r in vertical_spatial_relations_data:
            self._vertical_spatial_relations[_VerticalSpatialRelation[r]] = dict()
            for c in vertical_spatial_relations_data[r]:
                self._vertical_spatial_relations[_VerticalSpatialRelation[r]][c] = vertical_spatial_relations_data[r][c]
        self._used_unique_categories: List[str] = list()
        self._region: int = region

    def get_initialization_commands(self) -> List[dict]:
        self._used_unique_categories.clear()
        self.scene_bounds = None
        return [{"$type": "send_scene_regions"}]

    def on_send(self, resp: List[bytes]) -> None:
        if self.scene_bounds is None:
            self.scene_bounds = SceneBounds(resp=resp)

    @staticmethod
    def fits_inside_parent(parent: ModelRecord, child: ModelRecord) -> bool:
        """
        :param parent: The record of the parent object.
        :param child: The record of the child object.

        :return: True if the child object fits in the the parent object.
        """

        parent_extents = TDWUtils.get_bounds_extents(parent.bounds)
        child_extents = TDWUtils.get_bounds_extents(child.bounds)
        return parent_extents[0] > child_extents[0] and parent_extents[2] > child_extents[2]

    def model_fits_in_region(self, record: ModelRecord, position: Dict[str, float]) -> bool:
        """
        :param record: The model record.
        :param position: The position of the object.

        :return: True if the model fits in the region.
        """

        # Get the (x, z) positions of the bounds.
        for point in [[record.bounds["left"]["x"] + position["x"], record.bounds["left"]["z"] + position["z"]],
                      [record.bounds["right"]["x"] + position["x"], record.bounds["right"]["z"] + position["z"]],
                      [record.bounds["front"]["x"] + position["x"], record.bounds["front"]["z"] + position["z"]],
                      [record.bounds["back"]["x"] + position["x"], record.bounds["back"]["z"] + position["z"]],
                      [record.bounds["center"]["x"] + position["x"], record.bounds["center"]["z"] + position["z"]]]:
            if not self.scene_bounds.rooms[self._region].is_inside(x=point[0], z=point[1]):
                return False
        return True

    def get_model_that_fits_in_region(self, category: str, position: Dict[str, float]) -> Optional[ModelRecord]:
        """
        :param category: The model category.
        :param position: The position of the object.

        :return: A random model that fits in the region at `position`. If this returns None, no model fits.
        """

        model_names = ProcGenObjects.MODEL_CATEGORIES[category][:]
        self.rng.shuffle(model_names)
        # Get the first object, if any, that fits in the region bounds.
        got_model_name = False
        record = Controller.MODEL_LIBRARIANS["models_core.json"].records[0]
        for mn in model_names:
            record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(mn)
            if self.model_fits_in_region(record=record, position=position):
                got_model_name = True
                break
        if not got_model_name:
            return None
        else:
            return record

    def add_rotation_commands(self, parent_object_id: int, child_object_ids: List[int], rotation: float) -> None:
        """
        Add commands to parent the child objects to the parent object, rotate the parent object, and unparent the child objects.

        :param parent_object_id: The ID of the parent object.
        :param child_object_ids: The IDs of the child objects.
        :param rotation: The rotation of the parent object.
        """

        # Parent all objects to the root object.
        for child_object_id in child_object_ids:
            self.commands.append({"$type": "parent_object_to_object",
                                  "id": child_object_id,
                                  "parent_id": parent_object_id})
        # Rotate the root object.
        self.commands.append({"$type": "rotate_object_by",
                              "angle": rotation,
                              "id": parent_object_id,
                              "axis": "yaw",
                              "is_world": True,
                              "use_centroid": False})
        # Unparent all of the objects from the root object.
        for child_object_id in child_object_ids:
            self.commands.append({"$type": "unparent_object",
                                  "id": child_object_id})

    def add_rectangular_arrangement(self, size: Tuple[float, float], center: Union[np.array, Dict[str, float]],
                                    categories: List[str], density: float = 0.4, cell_size: float = 0.05) -> List[int]:
        """
        Get a random arrangement of objects in a rectangular space.

        :param size: The size of the rectangle in worldspace coordinates.
        :param center: The position of the center of the rectangle.
        :param categories: Models will be randomly chosen from these categories.
        :param density: The probability of a "cell" in the arrangement being empty. Lower value = a higher density of small objects.
        :param cell_size: The size of each cell in the rectangle. This controls the minimum size of objects and the density of the arrangement.

        :return: The IDs of the objects.
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
                model_size = TDWUtils.get_bounds_extents(bounds=record.bounds)
                model_semi_major_axis = model_size[0] if model_size[0] > model_size[2] else model_size[2]
                if model_semi_major_axis < semi_minor_axis:
                    model_sizes[model_name] = model_semi_major_axis
                    model_cell_sizes.append(int(model_semi_major_axis / cell_size) + 1)
                    models_and_categories[model_name] = category
        object_ids: List[int] = list()
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
            object_ids.append(object_id)
            if model_category in ProcGenObjects.KINEMATIC_CATEGORIES:
                object_rotation = 0
            else:
                object_rotation = self.rng.uniform(0, 360)
            # Add the object.
            self.commands.extend(Controller.get_add_physics_object(model_name=model_name,
                                                                   position={"x": x, "y": center_dict["y"], "z": z},
                                                                   rotation={"x": 0, "y": object_rotation, "z": 0},
                                                                   object_id=object_id,
                                                                   library="models_core.json"))
            # Record the position on the occupancy map.
            occupancy_map[TDWUtils.get_circle_mask(shape=(occupancy_map.shape[0], occupancy_map.shape[1]),
                                                   row=ix, column=iz, radius=sma) == True] = True
        return object_ids

    def add_object_with_other_objects_on_top(self, record: ModelRecord, category: str, position: Dict[str, float],
                                             rotation: float) -> None:
        """
        Add a root object and add objects on  top of it.

        :param record: The model record of the root object.
        :param category: The category of the root object.
        :param position: The position of the root object.
        :param rotation: The rotation of the root object.
        """

        model_size = TDWUtils.get_bounds_extents(bounds=record.bounds)
        root_object_id = Controller.get_unique_id()
        self.commands.extend(Controller.get_add_physics_object(model_name=record.name,
                                                               object_id=root_object_id,
                                                               position=position,
                                                               library="models_core.json",
                                                               kinematic=True))
        # Get the top position of the object.
        object_top = {"x": position["x"],
                      "y": record.bounds["top"]["y"] + position["y"],
                      "z": position["z"]}
        # Get the dimensions of the object's occupancy map.
        cell_size, density = self._get_rectangular_arrangement_parameters(category=category)
        surface_size = (model_size[0] * 0.8, model_size[2] * 0.8)
        # Add objects on top of the root object.
        object_ids = self.add_rectangular_arrangement(size=surface_size,
                                                      categories=self._vertical_spatial_relations[_VerticalSpatialRelation.on_top_of][category],
                                                      center=object_top,
                                                      cell_size=cell_size,
                                                      density=density)
        # Rotate everything.
        self.add_rotation_commands(parent_object_id=root_object_id, child_object_ids=object_ids, rotation=rotation)

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
    def _get_lateral_length(model_name: str) -> float:
        """
        :param model_name: The model name.

        :return: The model bound's longest extent.
        """

        record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(model_name)
        # Shelves are rotated 90 degrees.
        if record.name in ProcGenObjects.MODEL_CATEGORIES["shelf"]:
            return TDWUtils.get_bounds_extents(bounds=record.bounds)[2]
        else:
            return TDWUtils.get_bounds_extents(bounds=record.bounds)[0]

