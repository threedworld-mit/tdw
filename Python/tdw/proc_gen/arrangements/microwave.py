from typing import Dict, List, Union
import numpy as np
from tdw.container_data.box_container import BoxContainer
from tdw.container_data.container_tag import ContainerTag
from tdw.proc_gen.arrangements.arrangement_with_root_object import ArrangementWithRootObject
from tdw.proc_gen.arrangements.plate import Plate
from tdw.librarian import ModelRecord
from tdw.cardinal_direction import CardinalDirection


class Microwave(ArrangementWithRootObject):
    """
    A microwave can have objects on top of it and inside of it.

    - The microwave model is chosen randomly; see `Microwave.MODEL_CATEGORIES["microwave"]`
    - A microwave always has a rectangular arrangement of objects on top of it.
      - The objects are chosen randomly; see `Microwave.ON_TOP_OF["microwave"]`.
      - The objects are positioned in a rectangular grid on the microwave with random positional perturbations.
      - The objects have random rotations (0 to 360 degrees).
    - A microwave may have a [`Plate`](plate.md) inside it; see `plate_probability` in the constructor. The plate will always have food on it.
    - All microwaves have a door that can be opened.
    - The root object of the microwave is kinematic and the door sub-object is non-kinematic.
    """

    def __init__(self, plate_probability: float, wall: CardinalDirection, position: Dict[str, float],
                 model: Union[str, ModelRecord] = None, rng: np.random.RandomState = None):
        """
        :param plate_probability: The probability of placing a plate with food inside the microwave.
        :param wall: The wall as a [`CardinalDirection`](../../cardinal_direction.md) that the root object is next to.
        :param position: The position of the root object. This might be adjusted.
        :param model: Either the name of the model (in which case the model must be in `models_core.json`, or a `ModelRecord`, or None. If None, a random model in the category is selected.
        :param rng: The random number generator. If None, a new random number generator is created.
        """

        self._plate_probability: float = plate_probability
        self._wall: CardinalDirection = wall
        super().__init__(model=model, position=position, rng=rng)

    def get_commands(self) -> List[dict]:
        commands = self._add_object_with_other_objects_on_top(cell_size=0.05, density=0.4, rotate=False)
        # Add a plate with food.
        if self._rng.random() < self._plate_probability:
            # Get the inside container shape.
            for shape in self._record.container_shapes:
                if shape.tag == ContainerTag.enclosed and isinstance(shape, BoxContainer):
                    position, size = self._get_container_shape_position_and_size(shape=shape)
                    plate = Plate(food_probability=1,
                                  model="plate06",
                                  position=position,
                                  rng=self._rng)
                    commands.extend(plate.get_commands())
                    self.object_ids.extend(plate.object_ids)
        commands.extend(self._get_rotation_commands())
        return commands

    def _get_rotation(self) -> float:
        if self._wall == CardinalDirection.north:
            return 180
        elif self._wall == CardinalDirection.east:
            return 270
        elif self._wall == CardinalDirection.south:
            return 0
        else:
            return 90

    def _get_position(self, position: Dict[str, float]) -> Dict[str, float]:
        return position

    def _get_category(self) -> str:
        return "microwave"
