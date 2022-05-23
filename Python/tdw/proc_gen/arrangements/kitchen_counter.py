from json import loads
from pathlib import Path
from pkg_resources import resource_filename
from typing import Dict, List, Union, Optional
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller
from tdw.proc_gen.arrangements.kitchen_cabinet import KitchenCabinet
from tdw.proc_gen.arrangements.wall_cabinet import WallCabinet
from tdw.proc_gen.arrangements.microwave import Microwave
from tdw.proc_gen.arrangements.cabinetry.cabinetry import Cabinetry
from tdw.scene_data.interior_region import InteriorRegion
from tdw.cardinal_direction import CardinalDirection
from tdw.ordinal_direction import OrdinalDirection
from tdw.librarian import ModelRecord


class KitchenCounter(KitchenCabinet):
    """
    A kitchen counter can have objects on it and inside it.

    - The kitchen counter model is chosen randomly; see `KitchenCounter.MODEL_CATEGORIES["kitchen_counter"]`.
    - The kitchen counter is placed next to a wall.
      - The kitchen counter's position is automatically adjusted to set it flush to the wall.
      - The kitchen counter is automatically rotated so that it faces away from the wall.
    - A kitchen counter longer than 0.7 meters may have a [`Microwave`](microwave.md); see `allow_microwave` in the constructor.
        - If the kitchen counter is alongside a wall without windows and has a corresponding wall cabinet model, a [`WallCabinet`](wall_cabinet.md) will be added above it; see `KitchenCounter.COUNTERS_AND_CABINETS`.
        - The kitchen counter will have a rectangular arrangement of objects on top of it.
          - The objects are chosen randomly; see `KitchenCounter.ON_TOP_OF["kitchen_counter"]`.
          - The objects are positioned in a rectangular grid on the counter top with random rotations and positional perturbations; see `KitchenCounter.COUNTER_TOP_CELL_SIZE`, `KitchenCounter.COUNTER_TOP_CELL_DENSITY`, `KitchenCounter.COUNTER_TOP_WIDTH_SCALE`, and `KitchenCounter.COUNTER_TOP_DEPTH_SCALE`.
    - The interior of the kitchen counter may be empty; see `cabinet_is_empty_probability` in the constructor.
      - If the interior is _not_ empty, the kitchen counter will have a rectangular arrangement of objects inside its cabinet.
        - The objects are chosen randomly; see `KitchenCounter.ENCLOSED_BY["kitchen_counter"]`.
        - The objects are positioned in a rectangular grid inside the cabinet with random rotations and positional perturbations; see `KitchenCounter.CABINET_CELL_SIZE`, `KitchenCounter.CABINET_CELL_DENSITY`, `KitchenCounter.CABINET_WIDTH_SCALE`, and `KitchenCounter.CABINET_DEPTH_SCALE`.
    - All kitchen counters have doors that can open.
    - The root object of the kitchen counter is kinematic and the door sub-objects are non-kinematic.
    """

    """:class_var
    A dictionary of categories that can be on top of other categories. Key = A category. Value = A list of categories of models that can be on top of the key category.
    """
    COUNTERS_AND_CABINETS: Dict[str, str] = loads(Path(resource_filename(__name__, "data/counters_and_cabinets.json")).read_text())
    """:class_var
    The size of each cell in the counter top rectangular arrangement. This controls the minimum size of objects and the density of the arrangement.
    """
    COUNTER_TOP_CELL_SIZE: float = 0.05
    """:class_var
    The probability from 0 to 1 of a "cell" in the counter top rectangular arrangement being empty. Lower value = a higher density of small objects.
    """
    COUNTER_TOP_CELL_DENSITY: float = 0.4
    """:class_var
    When adding objects, the width of the counter top is assumed to be `actual_width * WIDTH_SCALE`. This prevents objects from being too close to the edges of the counter top.
    """
    COUNTER_TOP_WIDTH_SCALE: float = 0.8
    """:class_var
    When adding objects, the depth of the counter top is assumed to be `actual_depth * DEPTH_SCALE`. This prevents objects from being too close to the edges of the counter top.
    """
    COUNTER_TOP_DEPTH_SCALE: float = 0.8
    """:class_var
    The probability from 0 to 1 of a "cell" in the cabinet rectangular arrangement being empty. Lower value = a higher density of small objects.
    """
    CABINET_CELL_DENSITY: float = 0.1
    """:class_var
    The size of each cell in the cabinet rectangular arrangement. This controls the minimum size of objects and the density of the arrangement.
    """
    CABINET_CELL_SIZE: float = 0.04
    """:class_var
    When adding objects, the width of the cabinet is assumed to be `actual_width * CABINET_WIDTH_SCALE`. This prevents objects from being too close to the edges of the cabinet.
    """
    CABINET_WIDTH_SCALE: float = 0.7
    """:class_var
    When adding objects, the depth of the cabinet is assumed to be `actual_width * CABINET_DEPTH_SCALE`. This prevents objects from being too close to the edges of the cabinet.
    """
    CABINET_DEPTH_SCALE: float = 0.7

    def __init__(self, cabinetry: Cabinetry, corner: OrdinalDirection, wall: CardinalDirection, distance: float,
                 region: InteriorRegion, allow_microwave: bool = True, cabinet_is_empty_probability: float = 0.1,
                 microwave_model: Union[str, ModelRecord] = None, plate_model: Union[str, ModelRecord] = "plate06",
                 model: Union[str, ModelRecord] = None, wall_length: float = None,
                 rng: Union[int, np.random.RandomState] = None):
        """
        :param cabinetry: The [`Cabinetry`](cabinetry/cabinetry.md) set.
        :param wall: The wall as a [`CardinalDirection`](../../cardinal_direction.md) that the root object is next to.
        :param corner: The origin [`OrdinalDirection`](../../ordinal_direction.md) of this wall. This is used to derive the direction.
        :param distance: The distance in meters from the corner along the derived direction.
        :param region: The [`InteriorRegion`](../../scene_data/interior_region.md) that the object is in.
        :param allow_microwave: If True, and if this kitchen counter is longer than 0.7 meters, there will be a [`Microwave`](microwave.md) instead of an arrangement of objects on the counter top.
        :param cabinet_is_empty_probability: The probability (between 0 and 1) of the of the kitchen counter cabinet and wall cabinet being empty.
        :param model: Either the name of the model (in which case the model must be in `models_core.json`), or a `ModelRecord`, or None. If None, a model that fits along the wall at `distance` is randomly selected.
        :param wall_length: The total length of the lateral arrangement. If None, defaults to the length of the wall.
        :param rng: Either a random seed or an `numpy.random.RandomState` object. If None, a new random number generator is created.
        """

        self._allow_microwave: bool = allow_microwave
        """:field
        If True, this kitchen counter has a microwave.
        """
        self.has_microwave: bool = False
        self._cabinet_is_empty_probability: float = cabinet_is_empty_probability
        self._microwave_model: Optional[Union[str, ModelRecord]] = microwave_model
        self._plate_model: Union[str, ModelRecord] = plate_model
        super().__init__(cabinetry=cabinetry, corner=corner, wall=wall, distance=distance, region=region, model=model,
                         rng=rng, wall_length=wall_length)

    def get_commands(self) -> List[dict]:
        extents = TDWUtils.get_bounds_extents(bounds=self._record.bounds)
        # Place a microwave on top of the kitchen counter.
        if extents[0] > 0.7 and self._allow_microwave:
            commands = self._add_root_object()
            # Add objects in the cabinet.
            if self._rng.random() > self._cabinet_is_empty_probability:
                commands.extend(self._add_enclosed_objects(rotate=False,
                                                           density=KitchenCounter.CABINET_CELL_DENSITY,
                                                           cell_size=KitchenCounter.CABINET_CELL_SIZE,
                                                           x_scale=KitchenCounter.CABINET_WIDTH_SCALE,
                                                           z_scale=KitchenCounter.CABINET_DEPTH_SCALE))
            # Rotate everything.
            commands.extend(self._get_rotation_commands())
            # Add the microwave.
            microwave = Microwave(wall=self._wall,
                                  position={"x": self._position["x"],
                                            "y": self._record.bounds["top"]["y"] + self._position["y"],
                                            "z": self._position["z"]},
                                  rng=self._rng)
            commands.extend(microwave.get_commands())
            self.object_ids.extend(microwave.object_ids)
            self.has_microwave = True
            return commands
        else:
            # Add the kitchen counter and add objects on top of it.
            commands = self._add_object_with_other_objects_on_top(rotate=False,
                                                                  density=KitchenCounter.COUNTER_TOP_CELL_DENSITY,
                                                                  cell_size=KitchenCounter.COUNTER_TOP_CELL_SIZE,
                                                                  x_scale=KitchenCounter.COUNTER_TOP_WIDTH_SCALE,
                                                                  z_scale=KitchenCounter.COUNTER_TOP_DEPTH_SCALE)
            # Add objects in the cabinet.
            if self._rng.random() > self._cabinet_is_empty_probability:
                commands.extend(self._add_enclosed_objects(rotate=False,
                                                           density=KitchenCounter.CABINET_CELL_DENSITY,
                                                           cell_size=KitchenCounter.CABINET_CELL_SIZE,
                                                           x_scale=KitchenCounter.CABINET_DEPTH_SCALE,
                                                           z_scale=KitchenCounter.CABINET_DEPTH_SCALE))
            # Rotate everything.
            commands.extend(self._get_rotation_commands())
            # Add a wall cabinet.
            if self._record.name in KitchenCounter.COUNTERS_AND_CABINETS and \
                    self._region.walls_with_windows & self._wall == 0:
                wall_cabinet = WallCabinet(cabinetry=self._cabinetry,
                                           corner=self._corner,
                                           wall=self._wall,
                                           distance=self._distance,
                                           region=self._region,
                                           wall_length=self._wall_length,
                                           model=Controller.MODEL_LIBRARIANS["models_core.json"].get_record(
                                               KitchenCounter.COUNTERS_AND_CABINETS[self._record.name]),
                                           rng=self._rng)
                wall_cabinet_commands = wall_cabinet.get_commands()
                self.object_ids.extend(wall_cabinet.object_ids)
                commands.extend(wall_cabinet_commands)
            return commands

    def _get_category(self) -> str:
        return "kitchen_counter"

    def _get_model_names(self) -> List[str]:
        return self._cabinetry.kitchen_counters
