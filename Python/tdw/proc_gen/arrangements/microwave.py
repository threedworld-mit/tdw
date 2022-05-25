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
      - The objects are positioned in a rectangular grid on the microwave with random rotations and positional perturbations; see `Microwave.CELL_SIZE`, `Microwave.CELL_DENSITY`, `Microwave.WIDTH_SCALE`, and `Microwave.DEPTH_SCALE`.
    - A microwave may have a [`Plate`](plate.md) inside it; see `Microwave.PLATE_PROBABILITY`.
    - All microwaves have a door that can be opened.
    - The root object of the microwave is kinematic and the door sub-object is non-kinematic.
    """

    """:class_var
    The probability from 0 to 1 of placing a [`Plate`](plate.md) arrangement inside the microwave.
    """
    PLATE_PROBABILITY: float = 0.7
    """:class_var
    The model name of the plate that will be placed in the microwave (if any).
    """
    PLATE_MODEL: str = "plate06"
    """:class_var
    The size of each cell in the rectangular arrangement on top of the microwave. This controls the minimum size of objects and the density of the arrangement.
    """
    CELL_SIZE: float = 0.05
    """:class_var
    The probability from 0 to 1 of a "cell" in the rectangular arrangement  on top of the microwave being empty. Lower value = a higher density of small objects.
    """
    CELL_DENSITY: float = 0.4
    """:class
    When adding objects, the width of the top of the microwave is assumed to be `actual_width * WIDTH_SCALE`. This prevents objects from being too close to the edges of the microwave.
    """
    WIDTH_SCALE: float = 0.8
    """:class
    When adding objects, the depth of the top of the microwave is assumed to be `actual_depth * DEPTH_SCALE`. This prevents objects from being too close to the edges of the microwave.
    """
    DEPTH_SCALE: float = 0.8

    def __init__(self, wall: CardinalDirection, position: Dict[str, float], model: Union[str, ModelRecord] = None,
                 rng: Union[int, np.random.RandomState] = None):
        """
        :param wall: The wall as a [`CardinalDirection`](../../cardinal_direction.md) that the root object is next to.
        :param position: The position of the root object. This might be adjusted.
        :param model: Either the name of the model (in which case the model must be in `models_core.json`), or a `ModelRecord`, or None. If None, a random model in the category is selected.
        :param rng: Either a random seed or an `numpy.random.RandomState` object. If None, a new random number generator is created.
        """

        self._wall: CardinalDirection = wall
        super().__init__(model=model, position=position, rng=rng)

    def get_commands(self) -> List[dict]:
        commands = self._add_object_with_other_objects_on_top(cell_size=Microwave.CELL_SIZE,
                                                              density=Microwave.CELL_DENSITY,
                                                              x_scale=Microwave.WIDTH_SCALE,
                                                              z_scale=Microwave.DEPTH_SCALE,
                                                              rotate=False)
        # Add a plate with food.
        if self._rng.random() < Microwave.PLATE_PROBABILITY:
            # Get the inside container shape.
            for shape in self._record.container_shapes:
                if shape.tag == ContainerTag.enclosed and isinstance(shape, BoxContainer):
                    position, size = self._get_container_shape_position_and_size(shape=shape)
                    plate = Plate(model=Microwave.PLATE_MODEL,
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
