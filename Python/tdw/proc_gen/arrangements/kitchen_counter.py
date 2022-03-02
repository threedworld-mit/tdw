from json import loads
from pathlib import Path
from pkg_resources import resource_filename
from typing import Dict, List, Union
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.proc_gen.arrangements.kitchen_cabinet import KitchenCabinet
from tdw.proc_gen.arrangements.wall_cabinet import WallCabinet
from tdw.proc_gen.arrangements.microwave import Microwave
from tdw.proc_gen.arrangements.kitchen_cabinets.kitchen_cabinet_set import KitchenCabinetSet
from tdw.scene_data.interior_region import InteriorRegion
from tdw.cardinal_direction import CardinalDirection
from tdw.ordinal_direction import OrdinalDirection
from tdw.librarian import ModelRecord


class KitchenCounter(KitchenCabinet):
    """
    A kitchen counter can have objects on it, in it, and above it.

    - The kitchen counter model is chosen randomly; see `KitchenCounter.MODEL_CATEGORIES["kitchen_counter"]`.
    - The kitchen counter is placed next to a wall.
      - The kitchen counter's position is automatically adjusted to set it flush to the way.
      - The kitchen counter is automatically rotated so that it faces away from the wall.
    - A kitchen counter longer than 0.7 meters may have a [`Microwave`](microwave.md); see `allow_microwave` in the constructor.
    - If the kitchen counter does _not_ have a microwave:
      - If the kitchen counter is alongside a wall without windows and has a corresponding wall cabinet model, a [`WallCabinet`](wall_cabinet.md) will be added above it; see `KitchenCounter.COUNTERS_AND_CABINETS`.
      - The kitchen counter will have a rectangular arrangement of objects on top of it. The objects are chosen randomly; see `KitchenCounter.ON_TOP_OF["kitchen_counter"]`.
    - The interior of the kitchen counter may be empty; see `empty` in the constructor.
    - If the interior is _not_ empty, the kitchen counter will have a rectangular arrangement of objects inside of it. The objects are chosen randomly; see `KitchenCounter.ENCLOSED_BY["kitchen_counter"]`.
    - All kitchen counters have doors that can open.
    - The root object of the kitchen counter is kinematic and the door sub-objects are non-kinematic.
    """

    """:class_var
    A dictionary of categories that can be on top of other categories. Key = A category. Value = A list of categories of models that can be on top of the key category.
    """
    COUNTERS_AND_CABINETS: Dict[str, str] = loads(Path(resource_filename(__name__, "data/counters_and_cabinets.json")).read_text())

    def __init__(self, cabinetry: KitchenCabinetSet, corner: OrdinalDirection, wall: CardinalDirection, distance: float,
                 region: InteriorRegion, allow_microwave: bool = True, microwave_plate: float = 0.7, empty: float = 0.1,
                 model: Union[str, ModelRecord] = None, wall_length: float = None, rng: np.random.RandomState = None):
        """
        :param cabinetry: The [`KitchenCabinetSet`](kitchen_cabinets/kitchen_cabinet_set.md).
        :param wall: The wall as a [`CardinalDirection`](../../cardinal_direction.md) that the root object is next to.
        :param corner: The origin [`Corner`](../../corner.md) of this wall. This is used to derive the direction.
        :param distance: The distance in meters from the corner along the derived direction.
        :param region: The [`InteriorRegion`](../../scene_data/interior_region.md) that the object is in.
        :param allow_microwave: If True, and if this kitchen counter is longer than 0.7 meters, there will be a [`Microwave`](microwave.md) instead of an arrangement of objects on the counter top.
        :param microwave_plate: The probability (between 0 and 1) of adding a [`Plate`](plate.md) to the inside of the microwave.
        :param empty: The probability (between 0 and 1) of the of the kitchen counter being empty.
        :param model: Either the name of the model (in which case the model must be in `models_core.json`, or a `ModelRecord`, or None. If None, a model that fits along the wall at `distance` is randomly selected.
        :param wall_length: The total length of the lateral arrangement. If None, defaults to the length of the wall.
        :param rng: The random number generator. If None, a new random number generator is created.
        """

        self._allow_microwave: bool = allow_microwave
        """:field
        If True, this kitchen counter has a microwave.
        """
        self.has_microwave: bool = False
        self._microwave_plate: float = microwave_plate
        self._empty: float = empty
        self._min_num_plates: int = 3
        self._max_num_plates: int = 7
        super().__init__(cabinetry=cabinetry, corner=corner, wall=wall, distance=distance, region=region, model=model,
                         rng=rng, wall_length=wall_length)

    def _get_commands(self) -> List[dict]:
        extents = TDWUtils.get_bounds_extents(bounds=self._record.bounds)
        # Place a microwave on top of the kitchen counter.
        if extents[0] > 0.7 and self._allow_microwave:
            commands = self._add_root_object()
            # Add objects in the cabinet.
            if self._rng.random() > self._empty:
                commands.extend(self._add_enclosed_objects(rotate=False, density=0.1, cell_size=0.04))
            # Rotate everything.
            commands.extend(self._get_rotation_commands())
            # Add the microwave.
            microwave_model_names = self.MODEL_CATEGORIES["microwave"]
            microwave_model_name = microwave_model_names[self._rng.randint(0, len(microwave_model_names))]
            microwave = Microwave(plate_probability=self._microwave_plate,
                                  wall=self._wall,
                                  model=microwave_model_name,
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
            commands = self._add_object_with_other_objects_on_top(rotate=False)
            # Add objects in the cabinet.
            if self._rng.random() > self._empty:
                commands.extend(self._add_enclosed_objects(rotate=False, density=0.1, cell_size=0.04))
            # Rotate everything.
            commands.extend(self._get_rotation_commands())
            # Add a wall cabinet.
            if self._record.name in KitchenCounter.COUNTERS_AND_CABINETS and self._region.walls_with_windows & self._wall == 0:
                wall_cabinet = WallCabinet(cabinetry=self._cabinetry,
                                           corner=self._corner,
                                           wall=self._wall,
                                           distance=self._distance,
                                           region=self._region,
                                           wall_length=self._wall_length,
                                           model=KitchenCounter.COUNTERS_AND_CABINETS[self._record.name],
                                           rng=self._rng)
                wall_cabinet_commands = wall_cabinet.get_commands()
                self.object_ids.extend(wall_cabinet.object_ids)
                commands.extend(wall_cabinet_commands)
            return commands

    def _get_category(self) -> str:
        return "kitchen_counter"

    def _get_model_names(self) -> List[str]:
        return self._cabinetry.kitchen_counters
