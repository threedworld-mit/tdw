from json import loads
from pathlib import Path
from pkg_resources import resource_filename
from typing import Tuple, List, Union, Dict
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller
from tdw.librarian import ModelLibrarian, ModelRecord
from tdw.proc_gen_object_recipes.spatial_relation import SpatialRelation, SPATIAL_RELATIONS


class ProcGenObjectManager:

    # Cache the model librarian.
    if "models_core.json" not in Controller.MODEL_LIBRARIANS:
        Controller.MODEL_LIBRARIANS["models_core.json"] = ModelLibrarian("models_core.json")
    """:class_var
    The names of models suitable for proc-gen. Key = The category. Value = A list of model names.
    """
    MODEL_NAMES: Dict[str, List[str]] = loads(Path(resource_filename(__name__, "models.json")).read_text())
    """:class_var
    The appliance model categories. Objects in these categories won't have random rotations.
    """
    APPLIANCE_CATEGORIES: List[str] = Path(resource_filename(__name__, "appliances.txt")).read_text().split("\n")

    def __init__(self, random_seed: int = None):
        """
        :param random_seed: The random seed. If None, a random seed is randomly selected.
        """

        if random_seed is None:
            """:field
            The random number generator.
            """
            self.rng: np.random.RandomState = np.random.RandomState()
        else:
            self.rng = np.random.RandomState(random_seed)

    def get_relational_arrangement(self, category: str, position: Union[np.array, Dict[str, float]],
                                   rotation: float) -> List[dict]:
        assert category in ProcGenObjectManager.MODEL_NAMES, f"Invalid category: {category}"
        # Add the object.
        model_name = ProcGenObjectManager.MODEL_NAMES[category][self.rng.randint(0, len(ProcGenObjectManager.MODEL_NAMES[category]))]
        record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(model_name)
        if isinstance(position, dict):
            object_position = position
        elif isinstance(position, np.ndarray) or isinstance(position, list):
            object_position = TDWUtils.array_to_vector3(position)
        else:
            raise Exception(f"Invalid position argument: {position}")
        commands: List[dict] = Controller.get_add_physics_object(model_name=model_name,
                                                                 position=object_position,
                                                                 rotation={"x": 0, "y": rotation, "z": 0},
                                                                 library="models_core.json",
                                                                 object_id=Controller.get_unique_id(),
                                                                 kinematic=model_name in ProcGenObjectManager.APPLIANCE_CATEGORIES)
        # Get the size of the model.
        model_size = ProcGenObjectManager._get_size(record=record)
        # Add objects base on spatial relationship.
        for spatial_relation in SPATIAL_RELATIONS:
            if category not in SPATIAL_RELATIONS[spatial_relation]:
                continue
            # Put objects on top of the root object.
            if spatial_relation == SpatialRelation.on_top_of:
                # Gert the top position of the object.
                object_top = {"x": position["x"], "y": record.bounds["top"]["y"] + position["y"], "z": position["z"]}
                commands.extend(self.get_rectangular_arrangement(size=model_size,
                                                                 categories=SPATIAL_RELATIONS[spatial_relation][category],
                                                                 center=object_top,
                                                                 rotation=rotation))
        return commands

    def get_rectangular_arrangement(self, size: Tuple[float, float], center: Union[np.array, Dict[str, float]],
                                    categories: List[str], rotation: float = 0, probability_empty_cell: float = 0.4,
                                    cell_size: float = 0.05) -> List[dict]:
        """
        Get a random arrangement of objects in a rectangular space.

        :param size: The size of the rectangle in worldspace coordinates.
        :param center: The position of the center of the rectangle.
        :param categories: Models will be randomly chosen from these categories.
        :param rotation: Rotate the whole arrangement by this angle in degrees around the center position.
        :param probability_empty_cell: The probability of a "cell" in the arrangement being empty. Lower value = a higher density of small objects.
        :param cell_size: The size of each cell in the rectangle. This controls the minimum size of objects and the density of the arrangement.

        :return: Tuple: A list of commands to add the objects.
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
        # Get the x, z positions.
        xs: np.array = np.arange(cell_size, size[0] - cell_size, cell_size)
        zs: np.array = np.arange(cell_size, size[1] - cell_size, cell_size)
        # Get the occupancy map.
        occupancy_map: np.array = np.zeros(shape=(len(xs), len(zs)), dtype=bool)
        # Print a warning about bad categories.
        bad_categories = [c for c in categories if c not in ProcGenObjectManager.MODEL_NAMES]
        if len(bad_categories) > 0:
            print(f"WARNING! Invalid model categories: {bad_categories}")
        # Get the semi-minor axis of the rectangle's size.
        semi_minor_axis = (size[0] if size[0] < size[1] else size[1]) - (cell_size * 2)
        # Get valid objects.
        model_sizes: Dict[str, float] = dict()
        model_cell_sizes: List[int] = list()
        models_and_categories: Dict[str, str] = dict()
        for category in categories:
            if category not in ProcGenObjectManager.MODEL_NAMES:
                continue
            # Get objects small enough to fit within the rectangle.
            for model_name in ProcGenObjectManager.MODEL_NAMES[category]:
                record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(model_name)
                model_size = ProcGenObjectManager._get_size(record=record)
                model_semi_major_axis = model_size[0] if model_size[0] > model_size[1] else model_size[1]
                if model_semi_major_axis < semi_minor_axis:
                    model_sizes[model_name] = model_semi_major_axis
                    model_cell_sizes.append(int(model_semi_major_axis / cell_size) + 1)
                    models_and_categories[model_name] = category
        commands: List[dict] = list()
        # Get all of the sizes in occupancy map space.
        model_cell_sizes = list(set(model_cell_sizes))
        model_cell_sizes.reverse()
        for ix, iz in np.ndindex(occupancy_map.shape):
            # Exclude edges.
            if ix == 0 or ix == occupancy_map.shape[0] - 1 or iz == 0 or iz == occupancy_map.shape[1]:
                continue
            # This position is already occupied. Sometimes, skip a position.
            if occupancy_map[ix][iz] or self.rng.random() < probability_empty_cell:
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
            model_names = [m for m in model_sizes if int(model_sizes[m] / cell_size) + 1 <= sma]
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
            if model_category in ProcGenObjectManager.APPLIANCE_CATEGORIES:
                object_rotation = 0
            else:
                object_rotation = self.rng.uniform(0, 360)
            # Add the object.
            commands.extend(Controller.get_add_physics_object(model_name=model_name,
                                                              position={"x": x, "y": center_dict["y"], "z": z},
                                                              rotation={"x": 0, "y": object_rotation, "z": 0},
                                                              object_id=object_id,
                                                              library="models_core.json"))
            commands.append({"$type": "rotate_object_around",
                             "id": object_id,
                             "axis": "yaw",
                             "angle": rotation,
                             "position": center_dict})
            # Record the position on the occupancy map.
            occupancy_map[__get_circle_mask(circle_x=ix, circle_y=iz, radius=sma) == True] = True
        return commands

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
