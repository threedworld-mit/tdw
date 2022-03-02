from typing import List
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller
from tdw.cardinal_direction import CardinalDirection
from tdw.proc_gen.arrangements.arrangement_along_wall import ArrangementAlongWall
from tdw.container_data.container_collider_tag import ContainerColliderTag
from tdw.container_data.container_box_trigger_collider import ContainerBoxTriggerCollider


class Stove(ArrangementAlongWall):
    """
    A stove with oven doors.

    - For now, the stove model is always the same (`gas_stove_composite`).
    - The stove is placed next to a wall.
      - The stove's position is automatically adjusted to set it flush to the way.
      - The stove is automatically rotated so that it faces away from the wall.
    - The stove always has a rectangular arrangement of objects on top of it; see `Stove.ON_TOP_OF["stove"]`.
    - The stove has two doors that can open and two interior spaces.
    - 70% of the time, each of the interior spaces may have an object; see `Stove.ENCLOSED_BY["stove"]`.
    - The root object of the stove is non-kinematic and its door sub-objects are kinematic.
    """

    def get_commands(self) -> List[dict]:
        commands = self._add_object_with_other_objects_on_top(rotate=False)
        # Get all possible models that can be enclosed by the stove.
        enclose_by_model_names = []
        for category in Stove.ENCLOSED_BY["stove"]:
            for model_name in Stove.MODEL_CATEGORIES[category]:
                record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(model_name)
                model_size = TDWUtils.get_bounds_extents(bounds=record.bounds)
                model_semi_major_axis = model_size[0] if model_size[0] > model_size[2] else model_size[2]
                if model_semi_major_axis < 0.3:
                    enclose_by_model_names.append(model_name)
        # Try to add a model in each shelf.
        for collider in self._record.container_colliders:
            # Use all of the "enclosed" colliders.
            if collider.tag == ContainerColliderTag.enclosed and isinstance(collider, ContainerBoxTriggerCollider):
                if self._rng.random() < 0.7:
                    pos = self._get_collider_position(collider=collider)
                    pos["x"] += self._rng.uniform(-0.04, 0.04)
                    pos["z"] += self._rng.uniform(-0.04, 0.04)
                    object_id = Controller.get_unique_id()
                    commands.extend(Controller.get_add_physics_object(model_name=enclose_by_model_names[self._rng.randint(0, len(enclose_by_model_names))],
                                                                      object_id=object_id,
                                                                      position=pos,
                                                                      rotation={"x": 0, "y": self._rng.uniform(0, 360), "z": 0},
                                                                      library="models_core.json"))
                    self.object_ids.append(object_id)
        commands.extend(self._get_rotation_commands())
        return commands

    def get_length(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[2]

    def _get_depth(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[0] + 0.16595

    def _get_rotation(self) -> float:
        if self._wall == CardinalDirection.north:
            return 270
        elif self._wall == CardinalDirection.east:
            return 0
        elif self._wall == CardinalDirection.south:
            return 90
        else:
            return 180

    def _get_category(self) -> str:
        return "stove"
