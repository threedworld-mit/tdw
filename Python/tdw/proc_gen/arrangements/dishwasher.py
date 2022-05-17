from pathlib import Path
from json import loads
from pkg_resources import resource_filename
from typing import List, Dict, Tuple
from tdw.tdw_utils import TDWUtils
from tdw.cardinal_direction import CardinalDirection
from tdw.proc_gen.arrangements.arrangement_along_wall import ArrangementAlongWall
from tdw.controller import Controller
from tdw.librarian import ModelLibrarian


class Dishwasher(ArrangementAlongWall):
    """
    A dishwasher with a kitchen counter top with objects on it.

    - The dishwasher model is chosen randomly; see `Dishwasher.MODEL_CATEGORIES["dishwasher"]`.
    - The dishwasher is placed next to a wall.
      - The dishwasher's position is automatically adjusted to set it flush to the wall.
      - The dishwasher is automatically rotated so that it faces away from the wall.
      - The dishwasher's position along the wall is slightly offset; see `Dishwasher.LENGTH_OFFSET`.
    - The dishwasher has a floating kitchen counter top above it.
    - The floating kitchen counter top always has a rectangular arrangement of objects on top of it.
      - The objects are chosen randomly; see `Dishwasher.ON_TOP_OF["kitchen_counter"]`.
      - The objects are positioned in a rectangular grid on the dishwasher with random positional perturbations.
      - The objects have random rotations (0 to 360 degrees).
    - All dishwashers have a door that can be opened.
    - The root object of the dishwasher is kinematic and the door sub-object is non-kinematic.
    """

    """:class_var
    Offset the position and length of the dishwasher by this distance.
    """
    LENGTH_OFFSET: float = 0.025
    """:class_var
    A dictionary of counter top models per dishwasher model.
    """
    COUNTER_TOPS: Dict[str, str] = loads(Path(resource_filename(__name__, "data/dishwasher_counter_tops.json")).read_text())

    def get_commands(self) -> List[dict]:
        commands = self._add_root_object()
        # Add a counter top.
        if self._record.name in Dishwasher.COUNTER_TOPS:
            if "models_special.json" not in Controller.MODEL_LIBRARIANS:
                Controller.MODEL_LIBRARIANS["models_special.json"] = ModelLibrarian("models_special.json")
            counter_top_record = Controller.MODEL_LIBRARIANS["models_special.json"].get_record(Dishwasher.COUNTER_TOPS[self._record.name])
            counter_top_bounds = TDWUtils.get_bounds_extents(bounds=counter_top_record.bounds)
            counter_top_id = Controller.get_unique_id()
            commands.extend(Controller.get_add_physics_object(model_name=counter_top_record.name,
                                                              position=self._position,
                                                              rotation={"x": 0, "y": self._get_rotation(), "z": 0},
                                                              library="models_special.json",
                                                              object_id=counter_top_id,
                                                              kinematic=True))
            self.object_ids.append(counter_top_id)
            on_top_commands, object_ids = self._add_rectangular_arrangement(size=((counter_top_bounds[0] / 2) * 0.8,
                                                                                  (counter_top_bounds[1] / 2) * 0.8),
                                                                            categories=Dishwasher.ON_TOP_OF["kitchen_counter"],
                                                                            position={"x": self._position["x"],
                                                                                      "y": float(counter_top_bounds[1]),
                                                                                      "z": self._position["z"]})
            commands.extend(on_top_commands)
            commands.extend(self._get_rotation_commands())
        return commands

    def _get_position(self, position: Dict[str, float]) -> Dict[str, float]:
        pos = super()._get_position(position=position)
        # Offset the position to leave a little gap.
        if self._direction == CardinalDirection.north:
            pos["z"] += Dishwasher.LENGTH_OFFSET / 4
        elif self._direction == CardinalDirection.south:
            pos["z"] -= Dishwasher.LENGTH_OFFSET / 4
        elif self._direction == CardinalDirection.east:
            pos["x"] += Dishwasher.LENGTH_OFFSET / 4
        elif self._direction == CardinalDirection.west:
            pos["x"] -= Dishwasher.LENGTH_OFFSET / 4
        else:
            raise Exception(self._direction)
        return pos

    def get_length(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[0] + Dishwasher.LENGTH_OFFSET * 2

    def _get_rotation(self) -> float:
        if self._wall == CardinalDirection.north:
            return 180
        elif self._wall == CardinalDirection.east:
            return 270
        elif self._wall == CardinalDirection.south:
            return 0
        else:
            return 90

    def _get_depth(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[2]

    def _get_size(self) -> Tuple[float, float]:
        extents = TDWUtils.get_bounds_extents(bounds=self._record.bounds)
        return extents[2], extents[0] + Dishwasher.LENGTH_OFFSET * 2

    def _get_category(self) -> str:
        return "dishwasher"
