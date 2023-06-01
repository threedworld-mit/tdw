from json import loads
from pathlib import Path
from pkg_resources import resource_filename
from typing import Dict, List, Tuple, Union
from abc import ABC, abstractmethod
from overrides import final
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller
from tdw.librarian import ModelLibrarian


class Arrangement(ABC):
    """
    Abstract base class for procedurally-generated spatial arrangements of objects.
    """

    """:class_var
    A dictionary of all of the models that may be used for procedural generation. Key = The category. Value = A list of model names. Note that this category overlaps with, but is not the same as, `model_record.wcategory`; see: `Arrangement.get_categories_and_wcategories()`.
    """
    MODEL_CATEGORIES: Dict[str, List[str]] = loads(Path(resource_filename(__name__, "data/models.json")).read_text())
    """:class_var
    The default span used for arranging objects next to each other.
    """
    DEFAULT_CELL_SIZE: float = 0.6096

    def __init__(self, position: Dict[str, float], rng: Union[int, np.random.RandomState] = None):
        """
        :param position: The position of the root object. This might be adjusted.
        :param rng: Either a random seed or an `numpy.random.RandomState` object. If None, a new random number generator is created.
        """

        if rng is None:
            self._rng: np.random.RandomState = np.random.RandomState()
        elif isinstance(rng, int):
            self._rng = np.random.RandomState(rng)
        elif isinstance(rng, np.random.RandomState):
            self._rng = rng
        else:
            raise Exception(rng)
        self._position: Dict[str, float] = self._get_position(position={k: v for k, v in position.items()})
        self._rotation: float = self._get_rotation()
        """:field
        A list of all of the object IDs in this arrangement.
        """
        self.object_ids: List[int] = list()

    @staticmethod
    def get_categories_and_wcategories() -> Dict[str, Dict[str, str]]:
        """
        :return: A dictionary of the categories of every model that can be used by `Arrangement` and their corresponding `wcategory` and `wnid`. Key = The model name. Value = A dictionary with the following keys: `"category"` (the `ProcGenObjects` category), `"wcategory"` (the value of `record.wcategory`), and `"wnid"` (the value of `record.wnid`).
        """

        categories: Dict[str, Dict[str, str]] = dict()
        if "models_core.json" not in Controller.MODEL_LIBRARIANS:
            Controller.MODEL_LIBRARIANS["models_core.json"] = ModelLibrarian("models_core.json")
        for category in Arrangement.MODEL_CATEGORIES:
            for model_name in Arrangement.MODEL_CATEGORIES:
                record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(model_name)
                categories[model_name] = {"category": category,
                                          "wcategory": record.wcategory,
                                          "wnid": record.wnid}
        return categories

    @abstractmethod
    def get_commands(self) -> List[dict]:
        """
        :return: A list of commands that will generate the arrangement.
        """

        raise Exception()

    @abstractmethod
    def _get_position(self, position: Dict[str, float]) -> Dict[str, float]:
        """
        :param position: The original position.

        :return: The adjusted position of the object.
        """

        raise Exception()

    @abstractmethod
    def _get_rotation(self) -> float:
        """
        :return: The rotation of the root object.
        """

        raise Exception()

    @final
    def _add_rectangular_arrangement(self, size: Tuple[float, float], position: Dict[str, float], categories: List[str],
                                     density: float = 0.4, cell_size: float = 0.05,
                                     perturbation_distance: float = 0.01) -> Tuple[List[dict], List[int]]:
        """
        Get a random arrangement of objects in a rectangular space.

        :param size: The size of the rectangle in worldspace coordinates.
        :param position: The position of the center of the rectangle.
        :param categories: A list of potential model categories.
        :param density: The probability of a "cell" in the arrangement being empty. Lower value = a higher density of small objects.
        :param cell_size: The size of each cell in the rectangle. This controls the minimum size of objects and the density of the arrangement.
        :param perturbation_distance: Perturb the position of the objects by up to this distance.

        :return: Tuple: A list of commands, the IDs of the objects.
        """

        commands = []
        # Get the x, z positions.
        xs: np.ndarray = np.arange(cell_size, size[0] - cell_size, cell_size)
        zs: np.ndarray = np.arange(cell_size, size[1] - cell_size, cell_size)
        # Get the occupancy map.
        occupancy_map: np.ndarray = np.zeros(shape=(len(xs), len(zs)), dtype=bool)
        # Get the semi-minor axis of the rectangle's size.
        semi_minor_axis = size[0] if size[0] < size[1] else size[1]
        # Get valid objects.
        model_sizes: Dict[str, float] = dict()
        model_cell_sizes: List[int] = list()
        models_and_categories: Dict[str, str] = dict()
        for category in categories:
            # Get objects small enough to fit within the rectangle.
            for model_name in Arrangement.MODEL_CATEGORIES[category]:
                record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(model_name)
                model_size = TDWUtils.get_bounds_extents(bounds=record.bounds)
                model_semi_major_axis = model_size[0] if model_size[0] > model_size[2] else model_size[2]
                if model_semi_major_axis < semi_minor_axis:
                    model_sizes[model_name] = model_semi_major_axis
                    model_cell_sizes.append(int(model_semi_major_axis / cell_size) + 1)
                    models_and_categories[model_name] = category
        object_ids: List[int] = list()
        # Get all sizes in occupancy map space.
        model_cell_sizes = list(set(model_cell_sizes))
        model_cell_sizes.reverse()
        for ix, iz in np.ndindex(occupancy_map.shape[0], occupancy_map.shape[1]):
            # Exclude edges.
            if ix == 0 or ix == occupancy_map.shape[0] - 1 or iz == 0 or iz == occupancy_map.shape[1] - 1:
                continue
            # This position is already occupied. Sometimes, skip a position.
            if occupancy_map[ix][iz] or self._rng.random() < density:
                continue
            # Get the minimum object semi-major axis.
            sma = model_cell_sizes[0]
            for mcs in model_cell_sizes:
                # Stop if the semi-major axis doesn't fit (it would fall off the edge).
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
            model_name: str = model_names[self._rng.randint(0, len(model_names))]
            # Get the position. Perturb it slightly.
            x = (ix * cell_size) + self._rng.uniform(-cell_size * perturbation_distance,
                                                     cell_size * perturbation_distance)
            z = (iz * cell_size) + self._rng.uniform(-cell_size * perturbation_distance,
                                                     cell_size * perturbation_distance)
            # Offset from the center.
            x += position["x"] - size[0] / 2 + cell_size
            z += position["z"] - size[1] / 2 + cell_size
            # Cache the object ID.
            object_id = Controller.get_unique_id()
            # Set the rotation.
            object_ids.append(object_id)
            self.object_ids.append(object_id)
            # Add the object.
            commands.extend(Controller.get_add_physics_object(model_name=model_name,
                                                              position={"x": x, "y": position["y"], "z": z},
                                                              rotation={"x": 0, "y": self._rng.uniform(0, 360), "z": 0},
                                                              object_id=object_id,
                                                              library="models_core.json"))
            # Record the position on the occupancy map.
            occupancy_map[TDWUtils.get_circle_mask(shape=(occupancy_map.shape[0], occupancy_map.shape[1]),
                                                   row=ix, column=iz, radius=sma) == True] = True
        return commands, object_ids
