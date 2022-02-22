from typing import Dict, List
import numpy as np
from tdw.container_data.container_box_trigger_collider import ContainerBoxTriggerCollider
from tdw.container_data.container_collider_tag import ContainerColliderTag
from tdw.add_ons.proc_gen_objects_data.arrangement_with_root_object import ArrangementWithRootObject
from tdw.add_ons.proc_gen_objects_data.plate import Plate
from tdw.librarian import ModelRecord
from tdw.controller import Controller
from tdw.cardinal_direction import CardinalDirection


class Microwave(ArrangementWithRootObject):
    """
    A microwave always has a rectangular arrangement of objects on top of it; see `Microwave.ON_TOP_OF["microwave"]`.

    A microwave may have a [`Plate`](plate.md) inside it; see `plate_probability` in the constructor. The plate will always have food on it.

    The microwave model is chosen randomly; see `Microwave.MODEL_CATEGORIES["microwave"]`.

    Microwaves are kinematic but their sub-objects are non-kinematic.
    """

    def __init__(self, plate_probability: float, wall: CardinalDirection, record: ModelRecord,
                 position: Dict[str, float], rng: np.random.RandomState):
        """
        :param plate_probability: The probability of placing a plate with food inside the microwave.
        :param wall: The wall as a [`CardinalDirection`](../../cardinal_direction.md) that the root object is next to.
        :param record: The record of the root object.
        :param position: The position of the root object. This might be adjusted.
        :param rng: The random number generator.
        """

        self._plate_probability: float = plate_probability
        self._wall: CardinalDirection = wall
        super().__init__(record=record, position=position, rng=rng)

    def get_commands(self) -> List[dict]:
        commands = self._add_object_with_other_objects_on_top(cell_size=0.05, density=0.4, rotate=False)
        # Add a plate with food.
        if self._rng.random() < self._plate_probability:
            # Get the inside collider.
            for collider in self._record.container_colliders:
                if collider.tag == ContainerColliderTag.inside and isinstance(collider, ContainerBoxTriggerCollider):
                    plate = Plate(food_probability=1,
                                  record=Controller.MODEL_LIBRARIANS["models_core.json"].get_record("plate06"),
                                  position=self._get_collider_position(collider=collider),
                                  rng=self._rng)
                    commands.extend(plate.get_commands())
                    self.object_ids.extend(plate.object_ids)
        commands.extend(self._get_rotation_commands())
        return commands

    def _get_rotation(self) -> float:
        if self._wall == CardinalDirection.north:
            return 180
        elif self._wall == CardinalDirection.east:
            return 90
        elif self._wall == CardinalDirection.south:
            return 0
        else:
            return 270

    def _get_position(self, position: Dict[str, float]) -> Dict[str, float]:
        return position

    def _get_category(self) -> str:
        return "microwave"
