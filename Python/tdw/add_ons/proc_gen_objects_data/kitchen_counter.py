from json import loads
from pathlib import Path
from pkg_resources import resource_filename
from typing import Dict, List
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.proc_gen_objects_data.kitchen_cabinet import KitchenCabinet
from tdw.add_ons.proc_gen_objects_data.wall_cabinet import WallCabinet
from tdw.add_ons.proc_gen_objects_data.microwave import Microwave
from tdw.scene_data.interior_region import InteriorRegion
from tdw.cardinal_direction import CardinalDirection
from tdw.librarian import ModelRecord
from tdw.controller import Controller


class KitchenCounter(KitchenCabinet):
    """
    A kitchen counter can have objects on it, in it, and above it.

    A kitchen counter longer than 0.7 meters may have a [`Microwave`](microwave.md); see `allow_microwave` in the constructor.

    The microwave may have a [`Plate`](plate.md); see `microwave_plate` in the constructor. If it does have a plate, the plate always has food on it.

    If the kitchen counter does _not_ have a microwave:

      - If the kitchen counter is alongside a wall without windows and has a corresponding wall cabinet model, a [`WallCabinet`](wall_cabinet.md) will be added above it; see `KitchenCounter.COUNTERS_AND_CABINETS`.
      - The kitchen counter will have a rectangular arrangement of objects on top of it; see `KitchenCounter.ON_TOP_OF["kitchen_counter"]`.

    The interior of the kitchen counter may be empty; see `empty` in the constructor. If the interior is _not_ empty, the kitchen counter will have a rectangular arrangement of objects inside of it; see `KitchenCounter.ENCLOSED_BY["kitchen_counter"]`.
    """

    """:class_var
    A dictionary of categories that can be on top of other categories. Key = A category. Value = A list of categories of models that can be on top of the key category.
    """
    COUNTERS_AND_CABINETS: Dict[str, str] = loads(Path(resource_filename(__name__, "counters_and_cabinets.json")).read_text())

    def __init__(self, allow_microwave: bool, wall: CardinalDirection, region: InteriorRegion, record: ModelRecord, position: Dict[str, float],
                 rng: np.random.RandomState, microwave_plate: float = 0.7, empty: float = 0.15):
        """
        :param allow_microwave: If True, and if this kitchen counter is longer than 0.7 meters, there will be a [`Microwave`](microwave.md) instead of an arrangement of objects on the counter top.
        :param wall: The wall as a [`CardinalDirection`](../../cardinal_direction.md) that the root object is next to.
        :param region: The [`InteriorRegion`](../../scene_data/interior_region.md) that the object is in.
        :param record: The model record.
        :param position: The position of the root object. This might be adjusted.
        :param rng: The random number generator.
        :param microwave_plate: The probability (between 0 and 1) of adding a [`Plate`](plate.md) to the inside of the microwave.
        :param empty: The probability (between 0 and 1) of the of the kitchen counter being empty.
        """

        self._allow_microwave: bool = allow_microwave
        self.has_microwave: bool = False
        self._microwave_plate: float = microwave_plate
        self._empty: float = empty
        self._min_num_plates: int = 3
        self._max_num_plates: int = 7
        super().__init__(wall=wall, region=region, record=record, position=position, rng=rng)

    def get_commands(self) -> List[dict]:
        extents = TDWUtils.get_bounds_extents(bounds=self._record.bounds)
        # Place a microwave on top of the kitchen counter.
        if extents[0] < 0.7 and self._allow_microwave:
            root_object_id, commands = self._add_root_object()
            microwave_model_names = self.MODEL_CATEGORIES["microwave"]
            microwave_model_name = microwave_model_names[self._rng.randint(0, len(microwave_model_names))]
            microwave_record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(microwave_model_name)
            microwave = Microwave(plate_probability=self._microwave_plate,
                                  wall=self._wall,
                                  record=microwave_record,
                                  position={"x": self._position["x"],
                                            "y": self._record.bounds["top"]["y"] + self._position["y"],
                                            "z": self._position["z"]},
                                  rng=self._rng)
            commands.extend(microwave.get_commands())
            self.object_ids.extend(microwave.object_ids)
            commands.extend(self._get_rotation_commands())
            return commands
        else:
            # Add the kitchen counter and add objects on top of it.
            commands = self._add_object_with_other_objects_on_top(rotate=False)
            # Add objects in the cabinet.
            if self._rng.random() > self._empty:
                commands.extend(self._add_objects_inside(rotate=False))
            # Add a wall cabinet.
            if self._record.name in KitchenCounter.COUNTERS_AND_CABINETS and self._region.walls_with_windows & self._wall == 0:
                wall_cabinet = WallCabinet(wall=self._wall,
                                           region=self._region,
                                           record=Controller.MODEL_LIBRARIANS["models_core.json"].get_record(KitchenCounter.COUNTERS_AND_CABINETS[self._record.name]),
                                           position=self._position,
                                           rng=self._rng)
                wall_cabinet_commands = wall_cabinet.get_commands()
                self.object_ids.extend(wall_cabinet.object_ids)
                commands.extend(wall_cabinet_commands)
            # Rotate everything.
            commands.extend(self._get_rotation_commands())
            return commands

    def _get_category(self) -> str:
        return "kitchen_counter"
