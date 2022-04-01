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
      - The objects are positioned in a rectangular grid on the sink counter top with random positional perturbations.
      - The objects have random rotations (0 to 360 degrees).
    - The interior of the sink may be empty; see `empty` in the constructor.
      - If the interior is _not_ empty, the sink will have a rectangular arrangement of objects inside its cabinet.
        - The objects are chosen randomly; see `Sink.ENCLOSED_BY["sink"]`.
        - The objects are positioned in a rectangular grid in the sink cabinet with random positional perturbations.
        - The objects have random rotations (0 to 360 degrees).
    - There may be objects in the sink basin; see `Sink.IN_BASIN_PROBABILITY`.
      - The objects are chosen randomly; see `Sink.INSIDE_OF["sink"]`.
      - The objects are positioned in a rectangular grid in the sink basin with random positional perturbations.
      - The objects have random rotations (0 to 360 degrees).
    - All sinks have doors that can open.
    - The root object of the sink is kinematic and the door sub-objects are non-kinematic.
    """
    
    _FAUCETS = loads(Path(resource_filename(__name__, "data/faucets.json")).read_text())
    """:class_var
    The probability (0 to 1) of there being objects in the sink.
    """
    IN_BASIN_PROBABILITY: float = 0.7

    def get_commands(self) -> List[dict]:
        # Add objects on the counter top.
        commands = self._add_object_with_other_objects_on_top(rotate=False)
        # Add objects inside the cabinet.
        commands.extend(self._add_enclosed_objects(rotate=False))
        # Add objects in the sink basin.
        if self._rng.random() < Sink.IN_BASIN_PROBABILITY:
            commands.extend(self._add_inside_objects(rotate=False))
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
