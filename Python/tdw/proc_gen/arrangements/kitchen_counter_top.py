from typing import List
from tdw.proc_gen.arrangements.kitchen_cabinet import KitchenCabinet


class KitchenCounterTop(KitchenCabinet):
    """
    A floating kitchen counter top along a wall.

    - The kitchen counter top is placed next to a wall and at a height equal to the height of the kitchen counter models.
      - The kitchen counter top's position is automatically adjusted to set it flush to the wall.
    - The kitchen counter top will have a rectangular arrangement of objects on top of it.
      - The objects are chosen randomly; see `KitchenCounterTop.ON_TOP_OF["kitchen_counter"]`.
      - The objects are positioned in a rectangular grid on the counter top with random rotations and positional perturbations; see `KitchenCounterTop.CELL_SIZE`, `KitchenCounterTop.CELL_DENSITY`, `KitchenCounterTop.WIDTH_SCALE`, and `KitchenCounterTop.DEPTH_SCALE`.
    - The kitchen counter top is kinematic.
    """

    """:class_var
    The size of each cell in the counter top rectangular arrangement. This controls the minimum size of objects and the density of the arrangement.
    """
    CELL_SIZE: float = 0.05
    """:class_var
    The probability from 0 to 1 of a "cell" in the counter top rectangular arrangement being empty. Lower value = a higher density of small objects.
    """
    CELL_DENSITY: float = 0.4
    """:class
    When adding objects, the width of the counter top is assumed to be `actual_width * WIDTH_SCALE`. This prevents objects from being too close to the edges of the counter top.
    """
    WIDTH_SCALE: float = 0.8
    """:class
    When adding objects, the depth of the counter top is assumed to be `actual_depth * DEPTH_SCALE`. This prevents objects from being too close to the edges of the counter top.
    """
    DEPTH_SCALE: float = 0.8

    def _get_model_names(self) -> List[str]:
        return ["floating_counter_top_counter_top"]

    def _get_model_library(self) -> str:
        return "models_special.json"

    def get_commands(self) -> List[dict]:
        # Add the counter top if it fits in the region.
        if self._distance + KitchenCabinet.DEFAULT_CELL_SIZE < self._wall_length:
            return self._add_object_with_other_objects_on_top(cell_size=KitchenCounterTop.CELL_SIZE,
                                                              density=KitchenCounterTop.CELL_DENSITY,
                                                              x_scale=KitchenCounterTop.WIDTH_SCALE,
                                                              z_scale=KitchenCounterTop.DEPTH_SCALE)
        else:
            return []

    def _get_category(self) -> str:
        return "kitchen_counter"

    def _get_rotation(self) -> float:
        return super()._get_rotation() + 90
