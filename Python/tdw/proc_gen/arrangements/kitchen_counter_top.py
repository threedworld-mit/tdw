from typing import List
from tdw.proc_gen.arrangements.kitchen_cabinet import KitchenCabinet


class KitchenCounterTop(KitchenCabinet):
    """
    A floating kitchen counter top along a wall.

    - The kitchen counter top is placed next to a wall and at a height equal to the height of the kitchen counter models.
      - The kitchen counter top's position is automatically adjusted to set it flush to the wall.
    - The kitchen counter top will have a rectangular arrangement of objects on top of it.
      - The objects are chosen randomly; see `KitchenCounterTop.ON_TOP_OF["kitchen_counter"]`.
      - The objects are positioned in a rectangular grid on the counter top with random positional perturbations.
      - The objects have random rotations (0 to 360 degrees).
    - The kitchen counter top is kinematic.
    """

    def _get_model_names(self) -> List[str]:
        return ["floating_counter_top_counter_top"]

    def _get_model_library(self) -> str:
        return "models_special.json"

    def get_commands(self) -> List[dict]:
        # Add the counter top if it fits in the region.
        if self._distance + KitchenCabinet.DEFAULT_CELL_SIZE < self._wall_length:
            return self._add_object_with_other_objects_on_top()
        else:
            return []

    def _get_category(self) -> str:
        return "counter_top"
