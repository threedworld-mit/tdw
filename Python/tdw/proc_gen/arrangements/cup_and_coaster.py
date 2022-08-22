from typing import List, Dict
from tdw.controller import Controller
from tdw.proc_gen.arrangements.arrangement import Arrangement


class CupAndCoaster(Arrangement):
    """
    A cup, which sometimes has a coaster underneath it.

    - 50% of the time, there is a coaster underneath the cup.
      - The coaster model is chosen randomly; see `CupAndCoaster.MODEL_CATEGORIES["coaster"]`.
      - The coaster is rotated randomly; see `CupAndCoaster.ROTATION`.
    - The cup model is chosen randomly and can be either a `"cup"` or a `"wineglass"`; see `CupAndCoaster.MODEL_CATEGORIES["cup"]` and `CupAndCoaster.MODEL_CATEGORIES["wineglass"]`.
      - If there is a coaster, the cup is on top of the coaster.
      - The rotation of the cup is random (0 to 360 degrees).
    """

    """:class_var
    Coasters are randomly rotated up to +/- this many degrees.
    """
    ROTATION: float = 25
    """:class_var
    A list of cup model categories.
    """
    CUP_CATEGORIES: List[str] = ["cup", "wineglass"]

    def get_commands(self) -> List[dict]:
        commands = []
        # Add a coaster.
        if self._rng.random() > 0.5:
            coaster_model_name: str = CupAndCoaster.MODEL_CATEGORIES["coaster"][
                self._rng.randint(0, len(CupAndCoaster.MODEL_CATEGORIES["coaster"]))]
            coaster_id = Controller.get_unique_id()
            self.object_ids.append(coaster_id)
            commands.extend(Controller.get_add_physics_object(model_name=coaster_model_name,
                                                              position=self._position,
                                                              rotation={"x": 0,
                                                                        "y": float(self._rng.randint(
                                                                            -CupAndCoaster.ROTATION,
                                                                            CupAndCoaster.ROTATION)),
                                                                        "z": 0},
                                                              object_id=coaster_id,
                                                              library="models_core.json"))
            coaster_record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(coaster_model_name)
            y = self._position["y"] + coaster_record.bounds["top"]["y"]
        else:
            y = self._position["y"]
        # Add a cup or wine glass.
        cup_category = CupAndCoaster.CUP_CATEGORIES[self._rng.randint(0, len(CupAndCoaster.CUP_CATEGORIES))]
        cup_model_name = CupAndCoaster.MODEL_CATEGORIES[cup_category][self._rng.randint(0, len(CupAndCoaster.MODEL_CATEGORIES[cup_category]))]
        # Add the cup.
        cup_id = Controller.get_unique_id()
        self.object_ids.append(cup_id)
        commands.extend(Controller.get_add_physics_object(model_name=cup_model_name,
                                                          object_id=cup_id,
                                                          position={"x": self._position["x"],
                                                                    "y": y,
                                                                    "z": self._position["z"]},
                                                          rotation={"x": 0,
                                                                    "y": float(self._rng.uniform(0, 360)),
                                                                    "z": 0},
                                                          library="models_core.json"))
        return commands

    def _get_rotation(self) -> float:
        return 0

    def _get_position(self, position: Dict[str, float]) -> Dict[str, float]:
        return position
