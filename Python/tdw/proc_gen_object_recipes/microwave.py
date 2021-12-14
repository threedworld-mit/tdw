from typing import Dict, Tuple, List
from tdw.proc_gen_object_recipes.proc_gen_object_recipe import ProcGenObjectRecipe


class Microwave(ProcGenObjectRecipe):
    """
    A microwave can have things on top of it.
    """

    """:class_var
    The names and sizes (width, height, length) of microwaves.
    """
    MICROWAVE_MODEL_NAMES: Dict[str, Tuple[float, float, float]] = {'b05_whirlpool_microwave_wmc30516as_v-ray': (0.55, 0.33109224470348, 0.4300325),
                                                                    'cgaxis_models_10_11_vray': (0.5237763, 0.33200014470348, 0.406),
                                                                    'microwave': (0.5046881, 0.3106987, 0.27165438000000003),
                                                                    'vm_v5_070': (0.5181974, 0.28738972980232, 0.4461054)}
    """:class_var
    The names of items that can be on top of microwaves.
    """
    ITEM_MODEL_NAMES: List[str] = ["b03_loafbread", "bread"]
