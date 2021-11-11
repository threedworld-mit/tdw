from typing import List
from tdw.add_ons.add_on import AddOn

class ProcGenKitchen(AddOn):
    SCENE_NAMES: List[str] = ["mm_kitchen_1a", "mm_kitchen_1b"]
    WALL_WITHOUT_WINDOWS: dict = {'x': -3.0015454292297363,
                                  'z': [-3.483069896697998, 3.443080425262451]}

    CHAIR_MODEL_NAMES: List[str] = ['chair_billiani_doll', 'wood_chair', 'yellow_side_chair', 'chair_annabelle']
    TABLE_MODEL_NAMES: List[str] = ['enzo_industrial_loft_pine_metal_round_dining_table', 'quatre_dining_table']
    FLOOR_LAMP_MODEL_NAMES: List[str] = ["alma_floor_lamp", "bastone_floor_lamp", "bakerparisfloorlamp03"]
    SHELF_MODEL_NAME: str = "4ft_shelf_metal"
    MICROWAVE_MODEL_NAMES: List[str] = ["appliance-ge-profile-microwave3", "microwave"]

    HANDLE_MATERIAL_NAMES: List[str] = ["bronze_yellow", "steel_galvanized"]
    WOOD_MATERIAL_NAMES: List[str] = ["wood_oak_white", "wood_beech_honey"]
    COUNTERTOP_MATERIAL_NAMES: List[str] = ["granite_beige_french", "granite_black"]

    SHELF_ITEM_MODEL_NAMES: List[str] = ["duffle_bag_sm", "shoebox_fused", "basket_18inx18inx12iin_wicker",
                                         "box_18inx18inx12in_cardboard", "basket_18inx18inx12iin_wood_mesh",
                                         "basket_18inx18inx12iin_plastic_lattice"]
    #PANTRY_ITEM_NAMES: List[str]

    """:class_var
    Y values for each shelf in `4ft_shelf_metal`.
    """
    SHELF_YS: List[float] = [0.40797001123428345, 0.8050058484077454, 1.200427532196045]

    partnet_pantries = [41003, 41085, 45189, 45387]
    partnet_counters = [46014, 46109, 46380]
