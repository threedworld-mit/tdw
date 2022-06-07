from typing import List, Dict, Union
import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.proc_gen.arrangements.plate import Plate
from tdw.proc_gen.arrangements.cup_and_coaster import CupAndCoaster


class TableSetting(Plate):
    """
    A table setting includes a plate, fork, knife, spoon, and sometimes a cup.

    - This is a subclass of [`Plate`](plate.md). The plate model is always the same; see `TableSetting.PLATE_MODEL_NAME`.
    - The fork, knife, and spoon models are random; see `TableSetting.MODEL_CATEGORIES["fork"]`, `TableSetting.MODEL_CATEGORIES["knife"]`, and `TableSetting.MODEL_CATEGORIES["spoon"]`.
      - The rotations of the fork, knife, and spoon are perturbed randomly; see `TableSetting.CUTLERY_ROTATION_PERTURBATION`.
      - The positions of the fork, knife, and spoon are perturbed randomly; see `TableSetting.CUTLERY_POSITION_PERTURBATION`.
    - Sometimes, there is a [`CupAndCoaster`](cup_and_coaster.md); see `TableSetting.PROBABILITY_CUP_AND_COASTER`.
      - The position of the `CupAndCoaster` is perturbed randomly; see `TableSetting.CUP_AND_COASTER_POSITION_PERTURBATION`.
    """

    """:class_var
    The model name of the plate.
    """
    PLATE_MODEL_NAME: str = "plate06"
    """:class_var
    The probability from 0 to 1 of adding a [`CupAndCoaster`](cup_and_coaster.md).
    """
    PROBABILITY_CUP_AND_COASTER: float = 0.66
    """:class_var
    Randomly perturb the (x, z) positional coordinates of the fork, knife and spoon by up to +/- this distance.
    """
    CUTLERY_POSITION_PERTURBATION: float = 0.03
    """:class_var
    Randomly perturb the rotation of the fork, knife, and spoon by +/- this many degrees. 
    """
    CUTLERY_ROTATION_PERTURBATION: float = 3
    """:class_var
    Randomly perturb the (x, z) positional coordinates of `CupAndCoaster` by up to +/- this distance.
    """
    CUP_AND_COASTER_POSITION_PERTURBATION: float = 0.02

    def __init__(self, position: Dict[str, float], rng: Union[int, np.random.RandomState] = None):
        """
        :param position: The position of the root object. This might be adjusted.
        :param rng: Either a random seed or an `numpy.random.RandomState` object. If None, a new random number generator is created.
        """

        super().__init__(model=TableSetting.PLATE_MODEL_NAME, position=position, rng=rng)

    def get_commands(self) -> List[dict]:
        commands = super().get_commands()
        extents = TDWUtils.get_bounds_extents(bounds=self._record.bounds)
        fork_x = self._position["x"] - (extents[0] / 2 + self._rng.uniform(TableSetting.CUTLERY_POSITION_PERTURBATION,
                                                                           TableSetting.CUTLERY_POSITION_PERTURBATION))
        knife_x = self._position["x"] + extents[0] / 2 + self._rng.uniform(TableSetting.CUTLERY_POSITION_PERTURBATION,
                                                                           TableSetting.CUTLERY_POSITION_PERTURBATION)
        spoon_x = knife_x + self._rng.uniform(TableSetting.CUTLERY_POSITION_PERTURBATION,
                                              TableSetting.CUTLERY_POSITION_PERTURBATION)
        for category, x in zip(["fork", "knife", "spoon"], [fork_x, knife_x, spoon_x]):
            model_name = TableSetting.MODEL_CATEGORIES[category][self._rng.randint(0, len(TableSetting.MODEL_CATEGORIES[category]))]
            object_id = Controller.get_unique_id()
            self.object_ids.append(object_id)
            commands.extend(Controller.get_add_physics_object(model_name=model_name,
                                                              object_id=object_id,
                                                              position={"x": x,
                                                                        "y": self._position["y"],
                                                                        "z": self._position["z"] + self._rng.uniform(TableSetting.CUTLERY_POSITION_PERTURBATION,
                                                                                                                     TableSetting.CUTLERY_POSITION_PERTURBATION)},
                                                              rotation={"x": 0,
                                                                        "y": float(self._rng.uniform(
                                                                            -TableSetting.CUTLERY_ROTATION_PERTURBATION,
                                                                            TableSetting.CUTLERY_ROTATION_PERTURBATION)),
                                                                        "z": 0},
                                                              library="models_core.json"))
        # Add a cup.
        if self._rng.random() < TableSetting.PROBABILITY_CUP_AND_COASTER:
            cup_and_coaster = CupAndCoaster(position={"x": spoon_x + extents[0] * 0.45 + self._rng.uniform(
                -TableSetting.CUP_AND_COASTER_POSITION_PERTURBATION,
                TableSetting.CUP_AND_COASTER_POSITION_PERTURBATION),
                                                      "y": self._position["y"],
                                                      "z": self._position["z"] + extents[2] / 2 + self._rng.uniform(
                                                          -TableSetting.CUP_AND_COASTER_POSITION_PERTURBATION,
                                                          TableSetting.CUP_AND_COASTER_POSITION_PERTURBATION)},
                                            rng=self._rng)
            commands.extend(cup_and_coaster.get_commands())
            self.object_ids.extend(cup_and_coaster.object_ids)
        return commands
