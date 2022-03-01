from typing import List
from pathlib import Path
from pkg_resources import resource_filename
from json import loads
from tdw.controller import Controller
from tdw.proc_gen.arrangements.kitchen_cabinet import KitchenCabinet


class Sink(KitchenCabinet):
    _FAUCETS = loads(Path(resource_filename(__name__, "data/faucets.json")).read_text())

    def get_commands(self) -> List[dict]:
        # Add objects on the counter top.
        commands = self._add_object_with_other_objects_on_top(rotate=False)
        # Add objects inside the cabinet.
        commands.extend(self._add_enclosed_objects(rotate=False))
        # Add objects in the sink basin.
        if self._rng.random() < 0.7:
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
                                                            library="models_full.json",
                                                            kinematic=True)
        self.object_ids.append(faucet_id)
        commands.extend(faucet_commands)
        commands.extend(self._get_rotation_commands())
        commands.append({"$type": "rotate_object_by",
                         "angle": Sink._FAUCETS[faucet_model_name]["rotation"]["y"],
                         "id": faucet_id,
                         "axis": "yaw",
                         "is_world": True,
                         "use_centroid": False})
        return commands

    def _get_category(self) -> str:
        return "sink"
