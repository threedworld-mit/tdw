from json import loads
from pathlib import Path
from pkg_resources import resource_filename
from typing import Tuple, List, Dict, Optional
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller
from tdw.librarian import ModelLibrarian, ModelRecord
from tdw.add_ons.add_on import AddOn
from tdw.scene_data.scene_bounds import SceneBounds


class ProcGenObjects(AddOn):
    """
    Procedurally arrange objects using spatial relations and categories.
    For example, certain object categories can be *on top of* other object categories.

    Note regarding categories: Every "category" parameter *always* refers to specialized "proc-gen categories" that overlap with `record.wcategory` but are not the same. To get a mapping:

    ```python
    from tdw.add_ons.proc_gen_objects import ProcGenObjects

    categories = ProcGenObjects.get_categories_and_wcategories()
    for model_name in categories:
        print(model_name, categories[model_name]["category"], categories[model_name]["wcategory"], categories[model_name]["wnid"])
    ```
    """

    # Cache the model librarian.
    if "models_core.json" not in Controller.MODEL_LIBRARIANS:
        Controller.MODEL_LIBRARIANS["models_core.json"] = ModelLibrarian("models_core.json")
    """:class_var
    The names of models suitable for proc-gen. Key = The category. Value = A list of model names.
    """
    MODEL_CATEGORIES: Dict[str, List[str]] = loads(Path(resource_filename(__name__, "proc_gen_objects_data/models.json")).read_text())
    """:class_var
    Objects in these categories will be kinematic.
    """
    KINEMATIC_CATEGORIES: List[str] = Path(resource_filename(__name__, "proc_gen_objects_data/kinematic_categories.txt")).read_text().split("\n")
    """:class_var
    Parameters for rectangular arrangements. Key = Category. Value = Dictionary (`"cell_size"`, `"density"`).
    """
    RECTANGULAR_ARRANGEMENTS: Dict[str, dict] = loads(Path(resource_filename(__name__, "proc_gen_objects_data/rectangular_arrangements.json")).read_text())
    """:class_var
    The names of the models that are rotated 90 degrees.
    """
    MODEL_NAMES_NINETY_DEGREES: List[str] = Path(resource_filename(__name__, "proc_gen_objects_data/model_names_ninety_degrees.txt")).read_text().split("\n")
    """:class_var
    A dictionary of categories that can be on top of other categories. Key = A category. Value = A list of categories of models that can be on top of the key category.
    """
    ON_TOP_OF: Dict[str, List[str]] = loads(Path(resource_filename(__name__, "proc_gen_objects_data/on_top_of.json")).read_text())

    def __init__(self, random_seed: int = None, cell_size: float = 0.6096, print_random_seed: bool = True):
        """
        :param random_seed: The random seed. If None, a random seed is randomly selected.
        :param cell_size: The cell size in meters. This is also used to position certain objects in subclasses of `ProcGenObjects`.
        :param print_random_seed: If True, print the random seed. This can be useful for debugging.
        """

        super().__init__()
        self._print_random_seed: bool = print_random_seed
        if random_seed is None:
            """:field
            The random seed.
            """
            self.random_seed: int = Controller.get_unique_id()
        else:
            self.random_seed = random_seed
        if self._print_random_seed:
            print("Random seed: ", self.random_seed)
        """:field
        The random number generator.
        """
        self.rng = np.random.RandomState(self.random_seed)
        self._used_unique_categories: List[str] = list()
        """:field
        The [`SceneBounds`](../scene_data/scene_bounds.md). This is set after initializing or resetting `ProcGenObjects` and then calling `c.communicate()`.
        """
        self.scene_bounds: Optional[SceneBounds] = None
        """:field
        The cell size in meters. This is also used to position certain objects in subclasses of `ProcGenObjects`.
        """
        self.cell_size: float = cell_size

    def get_initialization_commands(self) -> List[dict]:
        """
        This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

        :return: A list of commands that will initialize this add-on.
        """

        return [{"$type": "send_scene_regions"}]

    def on_send(self, resp: List[bytes]) -> None:
        """
        This is called after commands are sent to the build and a response is received.

        Use this function to send commands to the build on the next frame, given the `resp` response.
        Any commands in the `self.commands` list will be sent on the next frame.

        :param resp: The response from the build.
        """

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

    def model_fits_in_region(self, record: ModelRecord, position: Dict[str, float], region: int) -> bool:
        """
        :param record: The model record.
        :param position: The position of the object.
        :param region: The index of the region in `self.scene_bounds.rooms`.

        :return: True if the model fits in the region.
        """

        # Get the (x, z) positions of the bounds.
        for point in [[record.bounds["left"]["x"] + position["x"], record.bounds["left"]["z"] + position["z"]],
                      [record.bounds["right"]["x"] + position["x"], record.bounds["right"]["z"] + position["z"]],
                      [record.bounds["front"]["x"] + position["x"], record.bounds["front"]["z"] + position["z"]],
                      [record.bounds["back"]["x"] + position["x"], record.bounds["back"]["z"] + position["z"]],
                      [record.bounds["center"]["x"] + position["x"], record.bounds["center"]["z"] + position["z"]]]:
            if not self.scene_bounds.rooms[region].is_inside(x=point[0], z=point[1]):
                return False
        return True

    def get_model_that_fits_in_region(self, category: str, position: Dict[str, float], region: int) -> Optional[ModelRecord]:
        """
        :param category: The model category.
        :param position: The position of the object.
        :param region: The index of the region in `self.scene_bounds.rooms`.

        :return: A random model that fits in the region at `position`. If this returns None, no model fits.
        """

        model_names = ProcGenObjects.MODEL_CATEGORIES[category][:]
        self.rng.shuffle(model_names)
        # Get the first object, if any, that fits in the region bounds.
        got_model_name = False
        record = Controller.MODEL_LIBRARIANS["models_core.json"].records[0]
        for mn in model_names:
            record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(mn)
            if self.model_fits_in_region(record=record, position=position, region=region):
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

    def add_rectangular_arrangement(self, size: Tuple[float, float], position: Dict[str, float],
                                    categories: List[str], density: float = 0.4, cell_size: float = 0.05) -> List[int]:
        """
        Get a random arrangement of objects in a rectangular space.

        :param size: The size of the rectangle in worldspace coordinates.
        :param position: The position of the center of the rectangle.
        :param categories: Models will be randomly chosen from these categories.
        :param density: The probability of a "cell" in the arrangement being empty. Lower value = a higher density of small objects.
        :param cell_size: The size of each cell in the rectangle. This controls the minimum size of objects and the density of the arrangement.

        :return: The IDs of the objects.
        """

        # Get numpy array and dictionary representations of the center position.
        if isinstance(position, dict):
            center_dict = position
        else:
            center_dict = TDWUtils.array_to_vector3(position)
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
        cell_size, density = self.get_rectangular_arrangement_parameters(category=category)
        surface_size = (model_size[0] * 0.8, model_size[2] * 0.8)
        # Add objects on top of the root object.
        object_ids = self.add_rectangular_arrangement(size=surface_size,
                                                      categories=ProcGenObjects.ON_TOP_OF[category],
                                                      position=object_top,
                                                      cell_size=cell_size,
                                                      density=density)
        # Rotate everything.
        self.add_rotation_commands(parent_object_id=root_object_id, child_object_ids=object_ids, rotation=rotation)

    def reset(self, set_random_seed: bool = False, random_seed: int = None) -> None:
        """
        Reset the procedural generator. Call this when resetting the scene.

        :param set_random_seed: If True, set a new random seed.
        :param random_seed: The random seed. If None, a random seed is randomly selected. Ignored if `set_random_seed == False`
        """

        self.initialized = False
        self._used_unique_categories.clear()
        self.scene_bounds = None
        if set_random_seed:
            if random_seed is None:
                self.random_seed = Controller.get_unique_id()
            else:
                self.random_seed = random_seed
            if self._print_random_seed:
                print("Random seed:", self.random_seed)
            self.rng = np.random.RandomState(self.random_seed)

    @staticmethod
    def get_categories_and_wcategories() -> Dict[str, Dict[str, str]]:
        """
        :return: A dictionary of the categories of every model that can be used by `ProcGenObjects`. Key = The model name. Value = A dictionary with the following keys: `"category"` (the `ProcGenObjects` category), `"wcategory"` (the value of `record.wcategory`), and `"wnid"` (the value of `record.wnid`).
        """

        categories: Dict[str, Dict[str, str]] = dict()
        for category in ProcGenObjects.MODEL_CATEGORIES:
            for model_name in ProcGenObjects.MODEL_CATEGORIES[category]:
                record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(model_name)
                categories[model_name] = {"category": category,
                                          "wcategory": record.wcategory,
                                          "wnid": record.wnid}
        return categories

    @staticmethod
    def get_rectangular_arrangement_parameters(category: str) -> Tuple[float, float]:
        """
        Given a category, get the default rectangular arrangement parameters.

        :param category: The category

        :return: Tuple: The cell size and density.
        """

        if category not in ProcGenObjects.RECTANGULAR_ARRANGEMENTS:
            return 0.05, 0.4
        return ProcGenObjects.RECTANGULAR_ARRANGEMENTS[category]["cell_size"], ProcGenObjects.RECTANGULAR_ARRANGEMENTS[category]["density"]

    @staticmethod
    def get_lateral_length(model_name: str) -> float:
        """
        :param model_name: The model name.

        :return: The model bound's longest extent.
        """

        record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(model_name)
        # Shelves are rotated 90 degrees.
        if record.name in ProcGenObjects.MODEL_NAMES_NINETY_DEGREES:
            ex = TDWUtils.get_bounds_extents(bounds=record.bounds)[2]
        else:
            ex = TDWUtils.get_bounds_extents(bounds=record.bounds)[0]
        return ex
