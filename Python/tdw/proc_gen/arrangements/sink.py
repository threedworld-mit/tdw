from typing import List
from pathlib import Path
from pkg_resources import resource_filename
from json import loads
from tdw.controller import Controller
from tdw.proc_gen.arrangements.kitchen_cabinet import KitchenCabinet


class Sink(KitchenCabinet):
    """
    A sink can have objects on it and inside it.

    - The sink model is chosen randomly; see `Sink.MODEL_CATEGORIES["sink"]`.
    - The sink is placed next to a wall.
      - The sink's position is automatically adjusted to set it flush to the wall.
      - The sink is automatically rotated so that it faces away from the wall.
    - The sink will have a rectangular arrangement of objects on the counter top.
      - The objects are chosen randomly; see `Sink.ON_TOP_OF["sink"]`.
      - The objects are positioned in a rectangular grid on the sink counter top with random rotations and positional perturbations; see `Sink.COUNTER_TOP_CELL_SIZE`, `Sink.COUNTER_TOP_CELL_DENSITY`, `Sink.COUNTER_TOP_WIDTH_SCALE`, and `Sink.COUNTER_TOP_DEPTH_SCALE`.
    - The interior of the sink may be empty; see `empty` in the constructor.
      - If the interior is _not_ empty, the sink will have a rectangular arrangement of objects inside its cabinet.
        - The objects are chosen randomly; see `Sink.ENCLOSED_BY["sink"]`.
        - The objects are positioned in a rectangular grid in the sink cabinet with random rotations and positional perturbations; see `Sink.CABINET_CELL_SIZE`, `Sink.CABINET_CELL_DENSITY`, `Sink.CABINET_WIDTH_SCALE`, and `Sink.CABINET_DEPTH_SCALE`.
    - There may be objects in the sink basin; see `Sink.IN_BASIN_PROBABILITY`.
      - The objects are chosen randomly; see `Sink.INSIDE_OF["sink"]`.
      - The objects are positioned in a rectangular arrangement in the sink basin; see: `Sink.BASIN_CELL_SIZE`, `Sink.BASIN_CELL_DENSITY`, `Sink.BASIN_WIDTH_SCALE`, and `Sink.BASIN_DEPTH_SCALE`.
    - All sinks have doors that can open.
    - The root object of the sink is kinematic and the door sub-objects are non-kinematic.
    """
    
    _FAUCETS = loads(Path(resource_filename(__name__, "data/faucets.json")).read_text())
    """:class_var
    The probability (0 to 1) of there being objects in the sink.
    """
    IN_BASIN_PROBABILITY: float = 0.7
    """:class_var
    The size of each cell in the counter top rectangular arrangement. This controls the minimum size of objects and the density of the arrangement.
    """
    COUNTER_TOP_CELL_SIZE: float = 0.05
    """:class_var
    The probability from 0 to 1 of a "cell" in the counter top rectangular arrangement being empty. Lower value = a higher density of small objects.
    """
    COUNTER_TOP_CELL_DENSITY: float = 0.4
    """:class_var
    When adding objects, the width of the counter top is assumed to be `actual_width * WIDTH_SCALE`. This prevents objects from being too close to the edges of the counter top.
    """
    COUNTER_TOP_WIDTH_SCALE: float = 0.8
    """:class_var
    When adding objects, the depth of the counter top is assumed to be `actual_depth * DEPTH_SCALE`. This prevents objects from being too close to the edges of the counter top.
    """
    COUNTER_TOP_DEPTH_SCALE: float = 0.8
    """:class_var
    The probability from 0 to 1 of a "cell" in the cabinet rectangular arrangement being empty. Lower value = a higher density of small objects.
    """
    CABINET_CELL_DENSITY: float = 0.1
    """:class_var
    The size of each cell in the cabinet rectangular arrangement. This controls the minimum size of objects and the density of the arrangement.
    """
    CABINET_CELL_SIZE: float = 0.04
    """:class_var
    When adding objects, the width of the cabinet is assumed to be `actual_width * CABINET_WIDTH_SCALE`. This prevents objects from being too close to the edges of the cabinet.
    """
    CABINET_WIDTH_SCALE: float = 0.7
    """:class_var
    When adding objects, the depth of the cabinet is assumed to be `actual_width * CABINET_DEPTH_SCALE`. This prevents objects from being too close to the edges of the cabinet.
    """
    CABINET_DEPTH_SCALE: float = 0.7
    """:class_var
    The size of each cell in the sink basin rectangular arrangement. This controls the minimum size of objects and the density of the arrangement.
    """
    BASIN_CELL_SIZE: float = 0.05
    """:class_var
    The probability from 0 to 1 of a "cell" in the sink basin rectangular arrangement being empty. Lower value = a higher density of small objects.
    """
    BASIN_CELL_DENSITY: float = 0.4
    """:class_var
    When adding objects, the width of the sink basin is assumed to be `actual_width * WIDTH_SCALE`. This prevents objects from being too close to the edges of the sink basin.
    """
    BASIN_WIDTH_SCALE: float = 0.8
    """:class_var
    When adding objects, the depth of the counter top is assumed to be `actual_depth * DEPTH_SCALE`. This prevents objects from being too close to the edges of the sink basin.
    """
    BASIN_DEPTH_SCALE: float = 0.8

    def get_commands(self) -> List[dict]:
        # Add objects on the counter top.
        commands = self._add_object_with_other_objects_on_top(rotate=False,
                                                              cell_size=Sink.COUNTER_TOP_CELL_SIZE,
                                                              density=Sink.COUNTER_TOP_CELL_DENSITY,
                                                              x_scale=Sink.COUNTER_TOP_WIDTH_SCALE,
                                                              z_scale=Sink.COUNTER_TOP_DEPTH_SCALE)
        # Add objects inside the cabinet.
        commands.extend(self._add_enclosed_objects(rotate=False,
                                                   cell_size=Sink.CABINET_CELL_SIZE,
                                                   density=Sink.CABINET_CELL_DENSITY,
                                                   x_scale=Sink.CABINET_WIDTH_SCALE,
                                                   z_scale=Sink.CABINET_DEPTH_SCALE))
        # Add objects in the sink basin.
        if self._rng.random() < Sink.IN_BASIN_PROBABILITY:
            commands.extend(self._add_inside_objects(rotate=False,
                                                     cell_size=Sink.BASIN_CELL_SIZE,
                                                     density=Sink.BASIN_CELL_DENSITY,
                                                     x_scale=Sink.COUNTER_TOP_WIDTH_SCALE,
                                                     z_scale=Sink.CABINET_DEPTH_SCALE))
        # Add the faucet.
        faucet_keys = list(Sink._FAUCETS.keys())
        faucet_model_name = faucet_keys[self._rng.randint(0, len(faucet_keys))]
        faucet_id = Controller.get_unique_id()
        faucet_commands = Controller.get_add_physics_object(model_name=faucet_model_name,
                                                            object_id=faucet_id,
                                                            position={"x": self._position["x"] + Sink._FAUCETS[faucet_model_name]["position"]["x"],
                                                                      "y": Sink._FAUCETS[faucet_model_name]["position"]["y"],
                                                                      "z": self._position["z"] + Sink._FAUCETS[faucet_model_name]["position"]["z"]},
                                                            rotation=Sink._FAUCETS[faucet_model_name]["rotation"],
                                                            kinematic=True)
        self.object_ids.append(faucet_id)
        commands.extend(faucet_commands)
        commands.extend(self._get_rotation_commands())
        return commands

    def _get_category(self) -> str:
        return "sink"

    def _get_model_names(self) -> List[str]:
        return self._cabinetry.sinks
