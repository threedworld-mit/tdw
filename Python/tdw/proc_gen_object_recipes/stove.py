from typing import List, Tuple, Dict
from tdw.proc_gen_object_recipes.proc_gen_object_recipe import ProcGenObjectRecipe


class Stove(ProcGenObjectRecipe):
    STOVE_SIZES: Dict[str, Tuple[float, float, float]] = {'b05_beko_oie_22500x_2013__corona': (0.5921968, 0.58794775960464, 0.5182700000000097),
                                                          'b05_max2013vray_oven_by_whirlpool_akzm8910ixl': (0.6000029, 0.599993, 0.5537239,),
                                                          'duhovka': (0.6000002, 0.46375107450581005, 0.6315914),
                                                          'vraymax2013_oven_akzm6610ixl_by_whirlpool': (0.6000027, 0.599993, 0.5537239)}

    """:class_var
    The names of pan models
    """
    PAN_MODEL_NAMES: List[str] = ["b03_696615_object001", "b03_object05",
                                  "int_kitchen_accessories_le_creuset_frying_pan_28cm", "measuring_pan", "object05",
                                  "pan01", "pan02", "pan03", "pan04", "pan05", "skillet_closed", "skillet_open_no_lid"]
    POT_MODEL_NAMES: List[str] = ["b03_aluminum_pan", "b03_cooking_pot_01", "pan1", "pan3", "pot"]



