from typing import List, Dict
import numpy as np
from tdw.controller import Controller
from tdw.add_ons.add_on import AddOn
from tdw.scene_data.scene_bounds import SceneBounds
from tdw.tdw_utils import TDWUtils


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



    partnet_pantries = [41003, 41085, 45189, 45387]
    partnet_counters = [46014, 46109, 46380]
    RNG: np.random.RandomState = np.random.RandomState()
    """:class_var
    The width of `4ft_shelf_metal` (derived from record bounds).
    """
    SHELF_WIDTH: float = 0.3857702
    """:class_var
    The length of `4ft_shelf_metal` (derived from record bounds).
    """
    SHELF_LENGTH: float = 0.9451682
    """:class_var
    Y values for each shelf in `4ft_shelf_metal`.
    """
    SHELF_YS: List[float] = [0.40797001123428345, 0.8050058484077454, 1.200427532196045]
    """:class_var
    Probability of there being an item on a shelf.
    """
    PROBABILITY_ITEM_ON_SHELF: float = 0.66

    def __init__(self, random_seed: int = None):
        super().__init__()
        # Set the RNG with a random seed.
        if random_seed is not None:
            ProcGenKitchen.RNG = np.random.RandomState(random_seed)

    @staticmethod
    def shelf(position: Dict[str, float], east_west: bool) -> List[dict]:
        """
        :param position: The position of the shelf.
        :param east_west: If True, the shelf is oriented east-west. If False, the shelf is oriented north-south.

        :return: A list of commands to add the shelf and place items on it.
        """

        # Add a shelf.
        if east_west:
            rotation = {"x": 0, "y": 0, "z": 0}
        else:
            rotation = {"x": 0, "y": 90, "z": 0}
        commands = Controller.get_add_physics_object(model_name="4ft_shelf_metal",
                                                     object_id=Controller.get_unique_id(),
                                                     library="models_core.json",
                                                     position=position,
                                                     rotation=rotation,
                                                     kinematic=True)
        # Add items on each shelf.
        for y in ProcGenKitchen.SHELF_YS:
            # Add an item on the shelf.
            if ProcGenKitchen.RNG.random() < ProcGenKitchen.PROBABILITY_ITEM_ON_SHELF:
                i = ProcGenKitchen.RNG.uniform(ProcGenKitchen.SHELF_WIDTH * 0.25, ProcGenKitchen.SHELF_WIDTH * 0.75) + \
                    position["x"]
                j = ProcGenKitchen.RNG.uniform(ProcGenKitchen.SHELF_LENGTH * 0.25, ProcGenKitchen.SHELF_LENGTH * 0.75) + \
                    position["z"]
                if east_west:
                    x = i
                    z = j
                else:
                    x = j
                    z = i
                commands.extend(Controller.get_add_physics_object(model_name=ProcGenKitchen.SHELF_ITEM_MODEL_NAMES[
                    ProcGenKitchen.RNG.randint(0, len(ProcGenKitchen.SHELF_ITEM_MODEL_NAMES))],
                                                                  object_id=Controller.get_unique_id(),
                                                                  library="models_core.json",
                                                                  position={"x": float(x), "y": y, "z": float(z)},
                                                                  rotation={"x": 0,
                                                                            "y": float(ProcGenKitchen.RNG.uniform(-45, 45)),
                                                                            "z": 0}))
        return commands

    @staticmethod
    def table(position: Dict[str, float], east_west: bool) -> List[dict]:
        """
        :param position: The position of the table.
        :param east_west:  If True, the table is oriented east-west. If False, the table is oriented north-south.

        :return: A list of commands to add a table and chairs around the table.
        """

        # Get a random table model name.
        table_name = ProcGenKitchen.TABLE_MODEL_NAMES[ProcGenKitchen.RNG.randint(0, len(ProcGenKitchen.TABLE_MODEL_NAMES))]
        # Add a table.
        if east_west:
            rotation = {"x": 0, "y": 0, "z": 0}
        else:
            rotation = {"x": 0, "y": 90, "z": 0}
        commands = Controller.get_add_physics_object(model_name=table_name,
                                                     object_id=Controller.get_unique_id(),
                                                     library="models_core.json",
                                                     position=position,
                                                     rotation=rotation,
                                                     kinematic=True)
        # Get the table record and its bounds positions.
        table_record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(table_name)
        table_bottom = {"x": table_record.bounds["bottom"]["x"] + position["x"],
                        "y": 0,
                        "z": table_record.bounds["bottom"]["z"] + position["z"]}
        table_bottom_arr = TDWUtils.array_to_vector3(table_bottom)
        # Get a random chair model name.
        chair_name = ProcGenKitchen.CHAIR_MODEL_NAMES[ProcGenKitchen.RNG.randint(0, len(ProcGenKitchen.CHAIR_MODEL_NAMES))]
        # Add chairs around the table.
        for bound in ["left", "right", "front", "back"]:
            table_bound_point = np.array([table_record.bounds[bound]["x"] + position["x"],
                                          0,
                                          table_record.bounds[bound]["z"] + position["z"]])
            chair_position = ProcGenKitchen.get_chair_position(table_bottom=table_bottom_arr,
                                                               table_bound_point=table_bound_point)
            object_id = Controller.get_unique_id()
            # Add the chair.
            commands.extend(Controller.get_add_physics_object(model_name=chair_name,
                                                              position=TDWUtils.array_to_vector3(chair_position),
                                                              object_id=object_id,
                                                              library="models_core.json"))
            # Look at the bottom-center and add a little rotation for spice.
            commands.extend([{"$type": "object_look_at_position",
                              "position": table_bottom,
                              "id": object_id},
                             {"$type": "rotate_object_by",
                              "angle": float(ProcGenKitchen.RNG.uniform(-20, 20)),
                              "id": object_id,
                              "axis": "yaw"}])
        return commands

    @staticmethod
    def get_chair_position(table_bottom: np.array, table_bound_point: np.array) -> np.array:
        """
        :param table_bottom: The bottom-center position of the table.
        :param table_bound_point: The bounds position.

        :return: A position for a chair around the table.
        """

        position_to_center = table_bound_point - table_bottom
        position_to_center_normalized = position_to_center / np.linalg.norm(position_to_center)
        chair_position = table_bound_point + (position_to_center_normalized * ProcGenKitchen.RNG.uniform(0.5, 0.125))
        chair_position[1] = 0
        return chair_position
