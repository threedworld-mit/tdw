from typing import List
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller
from tdw.cardinal_direction import CardinalDirection
from tdw.proc_gen.arrangements.arrangement_along_wall import ArrangementAlongWall
from tdw.container_data.container_tag import ContainerTag
from tdw.container_data.box_container import BoxContainer


class Stove(ArrangementAlongWall):
    """
    A stove with oven doors.

    - For now, the stove model is always the same (`gas_stove_composite`).
    - The stove is placed next to a wall.
      - The stove's position is automatically adjusted to set it flush to the wall plus an offset; see `Stove.DEPTH_OFFSET`.
      - The stove is automatically rotated so that it faces away from the wall.
    - The stove always has a rectangular arrangement of objects on top of it; see `Stove.ON_TOP_OF["stove"]`
      - The objects are chosen randomly; see `Stove.ON_TOP_OF["stove"]`.
      - The objects are positioned in a rectangular grid on the stove with random rotations and positional perturbations; see: `Stove.CELL_SIZE`, `Stove.CELL_DENSITY`, `Stove.WIDTH_SCALE`, and `Stove.DEPTH_SCALE`.
    - The stove has two doors that can open and two interior spaces.
    - Sometimes, each of the interior spaces may have one object; see `Stove.PROBABILITY_INSIDE` and `Stove.ENCLOSED_BY["stove"]`.
      - The positions of the object(s) are perturbed randomly, see `Stove.INSIDE_POSITION_PERTURBATION`.
      - The rotation of the object(s) is random (0 to 360 degrees).
    - The root object of the stove is non-kinematic and its door sub-objects are kinematic.
    """

    """:class_var
    Offset the stove from the wall by this distance.
    """
    DEPTH_OFFSET: float = 0.16595
    """:class_var
    The probability (0 to 1) of adding objects inside each interior space of the stove.
    """
    PROBABILITY_INSIDE: float = 0.7
    """:class_var
    The (x, z) positional coordinates of objects inside the stove will be randomly perturbed by up to +/- this value.
    """
    INSIDE_POSITION_PERTURBATION: float = 0.04
    """:class_var
    The size of each cell in the stove top rectangular arrangement. This controls the minimum size of objects and the density of the arrangement.
    """
    CELL_SIZE: float = 0.05
    """:class_var
    The probability from 0 to 1 of a "cell" in the stove top rectangular arrangement being empty. Lower value = a higher density of small objects.
    """
    CELL_DENSITY: float = 0.4
    """:class
    When adding objects, the width of the stove top is assumed to be `actual_width * WIDTH_SCALE`. This prevents objects from being too close to the edges of the stove top.
    """
    WIDTH_SCALE: float = 0.8
    """:class
    When adding objects, the depth of the stove top is assumed to be `actual_depth * DEPTH_SCALE`. This prevents objects from being too close to the edges of the stove top.
    """
    DEPTH_SCALE: float = 0.8

    def get_commands(self) -> List[dict]:
        commands = self._add_object_with_other_objects_on_top(rotate=False,
                                                              cell_size=Stove.CELL_SIZE,
                                                              density=Stove.CELL_DENSITY,
                                                              x_scale=Stove.WIDTH_SCALE,
                                                              z_scale=Stove.DEPTH_SCALE)
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
        for shape in self._record.container_shapes:
            # Use all of the "enclosed" shapes.
            if shape.tag == ContainerTag.enclosed and isinstance(shape, BoxContainer):
                if self._rng.random() < Stove.PROBABILITY_INSIDE:
                    position, size = self._get_container_shape_position_and_size(shape=shape)
                    position["x"] += self._rng.uniform(-Stove.INSIDE_POSITION_PERTURBATION, Stove.INSIDE_POSITION_PERTURBATION)
                    position["z"] += self._rng.uniform(-Stove.INSIDE_POSITION_PERTURBATION, Stove.INSIDE_POSITION_PERTURBATION)
                    object_id = Controller.get_unique_id()
                    commands.extend(Controller.get_add_physics_object(model_name=enclose_by_model_names[self._rng.randint(0, len(enclose_by_model_names))],
                                                                      object_id=object_id,
                                                                      position=position,
                                                                      rotation={"x": 0, "y": self._rng.uniform(0, 360), "z": 0},
                                                                      library="models_core.json"))
                    self.object_ids.append(object_id)
        commands.extend(self._get_rotation_commands())
        return commands

    def get_length(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[2]

    def _get_depth(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[0] + Stove.DEPTH_OFFSET

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
