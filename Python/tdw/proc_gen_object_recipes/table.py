from typing import List, Dict
import numpy as np
from tdw.proc_gen_object_recipes.proc_gen_object_recipe import ProcGenObjectRecipe
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.proc_gen_object_recipes.kitchen_set import KitchenSet


class Table(ProcGenObjectRecipe):
    """
    A table with chairs and, optionally, table settings.
    """

    """:class_var
    Table model names.
    """
    TABLE_MODEL_NAMES: List[str] = ['enzo_industrial_loft_pine_metal_round_dining_table']
    """:class_var
    Chair model names.
    """
    CHAIR_MODEL_NAMES: List[str] = ['chair_billiani_doll', 'wood_chair', 'yellow_side_chair', 'chair_annabelle']
    """:class_var
    Food model names.
    """
    FOOD_MODEL_NAMES: List[str] = ["b03_banana_01_high", "b03_burger", "b03_pain_au_chocolat"]
    """:class_var
    Centerpiece model names.
    """
    CENTERPIECE_MODEL_NAMES: List[str] = ['round_bowl_small_walnut', 'vase_01', 'vase_02', 'vase_03', 'vase_05',
                                          'vase_06', 'pot', 'jug01', 'jug02', 'jug03', 'jug04', 'jug05',
                                          'skillet_closed', 'skillet_open_no_lid']
    """:class_var
    The height of the plate model.
    """
    PLATE_HEIGHT: float = 0.02264883

    def __init__(self, position: Dict[str, float], north_south: bool, rng: np.random.RandomState = None,
                 table_settings: bool = True, kitchen_set: KitchenSet = None):
        """
        :param position: The position of the object.
        :param north_south: If True, the object is aligned north-south (0 degree rotation). If False, the object is aligned east-west (90 degree rotation).
        :param rng: The random number generator. If None, a generator is created.
        :param table_settings: If True, add table settings (plates, forks, knives, etc.).
        :param kitchen_set: The [`KitchenSet`](kitchen_set.md). If None, a kitchen set is randomly generated. Ignored if `table_settings == False`.
        """

        super().__init__(position=position, north_south=north_south, rng=rng)
        self._table_settings: bool = table_settings
        if kitchen_set is None:
            self._kitchen_set: KitchenSet = KitchenSet()
        else:
            self._kitchen_set = kitchen_set

    def create(self) -> List[dict]:
        # Get a random table model name.
        table_name = Table.TABLE_MODEL_NAMES[self._rng.randint(0, len(Table.TABLE_MODEL_NAMES))]
        # Add the table.
        commands = Controller.get_add_physics_object(model_name=table_name,
                                                     object_id= Controller.get_unique_id(),
                                                     library="models_core.json",
                                                     position=self.position,
                                                     rotation={"x": 0, "y": 0 if self.north_south else 90, "z": 0},
                                                     kinematic=True)
        # Get the table record and its bounds positions.
        table_record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(table_name)
        table_bottom = {"x": table_record.bounds["bottom"]["x"] + self.position["x"],
                        "y": 0,
                        "z": table_record.bounds["bottom"]["z"] + self.position["z"]}
        table_bottom_arr = TDWUtils.vector3_to_array(table_bottom)
        table_top_arr = TDWUtils.vector3_to_array(table_record.bounds["top"])
        # Get a random chair model name.
        chair_name = Table.CHAIR_MODEL_NAMES[self._rng.randint(0, len(Table.CHAIR_MODEL_NAMES))]
        # Add chairs around the table.
        for bound in ["left", "right", "front", "back"]:
            table_bound_point = np.array([table_record.bounds[bound]["x"] + self.position["x"],
                                          0,
                                          table_record.bounds[bound]["z"] + self.position["z"]])
            chair_position = Table._get_chair_position(table_bottom=table_bottom_arr,
                                                       table_bound_point=table_bound_point,
                                                       rng=self._rng)
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
                              "angle": float(self._rng.uniform(-20, 20)),
                              "id": object_id,
                              "axis": "yaw"}])
        # Add table settings.
        if self._table_settings:
            for bound in ["left", "right", "front", "back"]:
                table_bound_point = np.array([table_record.bounds[bound]["x"] + self.position["x"],
                                              0,
                                              table_record.bounds[bound]["z"] + self.position["z"]])
                # Get the position of the plate. Use this as a reference for all other objects.
                plate_position = self._get_plate_position(table_top=table_top_arr,
                                                          table_bound_point=table_bound_point,
                                                          rng=self._rng)
                # Add the plate.
                commands.extend(Controller.get_add_physics_object(model_name=KitchenSet.PLATE,
                                                                  position=TDWUtils.array_to_vector3(plate_position),
                                                                  object_id=Controller.get_unique_id(),
                                                                  library="models_core.json"))
                # Get the direction from the plate to the center.
                v = np.array([self.position["x"], self.position["z"]]) - np.array([plate_position[0], plate_position[2]])
                v / np.linalg.norm(v)
                fork_position = self._get_fork_position(plate_position=plate_position, v=v, rng=self._rng)
                knife_position = self._get_knife_position(plate_position=plate_position, v=v, rng=self._rng)
                spoon_position = self._get_spoon_position(plate_position=plate_position, v=v, rng=self._rng)
                # Get the rotation of the fork, knife, and spoon.
                if bound == "left":
                    rotation = 90
                elif bound == "right":
                    rotation = 270
                elif bound == "front":
                    rotation = 180
                else:
                    rotation = 0
                # Add a fork.
                commands.extend(Controller.get_add_physics_object(model_name=self._kitchen_set.fork,
                                                                  object_id=Controller.get_unique_id(),
                                                                  position=TDWUtils.array_to_vector3(fork_position),
                                                                  rotation={"x": 0,
                                                                            "y": rotation + float(self._rng.uniform(-15, 15)),
                                                                            "z": 0},
                                                                  library="models_core.json"))
                # Add a knife.
                commands.extend(Controller.get_add_physics_object(model_name=self._kitchen_set.knife,
                                                                  object_id=Controller.get_unique_id(),
                                                                  position=TDWUtils.array_to_vector3(knife_position),
                                                                  rotation={"x": 0,
                                                                            "y": rotation + float(self._rng.uniform(-15, 15)),
                                                                            "z": 0},
                                                                  library="models_core.json"))
                # Add a spoon.
                commands.extend(Controller.get_add_physics_object(model_name=self._kitchen_set.spoon,
                                                                  object_id=Controller.get_unique_id(),
                                                                  position=TDWUtils.array_to_vector3(spoon_position),
                                                                  rotation={"x": 0,
                                                                            "y": rotation + float(self._rng.uniform(-15, 15)),
                                                                            "z": 0},
                                                                  library="models_core.json"))
                cup_position = self._get_cup_position(plate_position=plate_position, v=v, rng=self._rng)
                cup_roll = self._rng.random()
                # Add a mug.
                if cup_roll < 0.33:
                    commands.extend(Controller.get_add_physics_object(model_name=self._kitchen_set.MUG,
                                                                      object_id=Controller.get_unique_id(),
                                                                      position=TDWUtils.array_to_vector3(cup_position),
                                                                      rotation={"x": 0,
                                                                                "y": rotation + float(
                                                                                    self._rng.uniform(0, 360)),
                                                                                "z": 0},
                                                                      library="models_core.json"))
                # Add a wine glass.
                elif cup_roll < 0.66:
                    commands.extend(Controller.get_add_physics_object(model_name=self._kitchen_set.wine_glass,
                                                                      object_id=Controller.get_unique_id(),
                                                                      position=TDWUtils.array_to_vector3(cup_position),
                                                                      rotation={"x": 0,
                                                                                "y": rotation + float(
                                                                                    self._rng.uniform(0, 360)),
                                                                                "z": 0},
                                                                      library="models_core.json"))
                # Add food.
                if self._rng.random() < 0.66:
                    food_model_name: str = self._rng.choice(Table.FOOD_MODEL_NAMES)
                    food_position = [plate_position[0] + self._rng.uniform(-0.05, 0.05),
                                     plate_position[1] + Table.PLATE_HEIGHT,
                                     plate_position[2] + self._rng.uniform(-0.05, 0.05)]
                    commands.extend(Controller.get_add_physics_object(model_name=food_model_name,
                                                                      object_id=Controller.get_unique_id(),
                                                                      position=TDWUtils.array_to_vector3(food_position),
                                                                      rotation={"x": 0,
                                                                                "y": rotation + float(
                                                                                    self._rng.uniform(0, 360)),
                                                                                "z": 0},
                                                                      library="models_core.json"))
        # Add a centerpiece.
        if self._rng.random() < 0.75:
            commands.extend(Controller.get_add_physics_object(model_name=self._rng.choice(Table.CENTERPIECE_MODEL_NAMES),
                                                              object_id=Controller.get_unique_id(),
                                                              position={"x": self.position["x"] + float(self._rng.uniform(-0.1, 0.1)),
                                                                        "y": float(table_top_arr[1]),
                                                                        "z": self.position["z"] + float(self._rng.uniform(-0.1, 0.1))},
                                                              rotation={"x": 0,
                                                                        "y": float(self._rng.uniform(0, 360)),
                                                                        "z": 0},
                                                              library="models_core.json"))
        return commands

    @staticmethod
    def _get_chair_position(table_bottom: np.array, table_bound_point: np.array,
                            rng: np.random.RandomState) -> np.array:
        """
        :param table_bottom: The bottom-center position of the table.
        :param table_bound_point: The bounds position.
        :param rng: The random number generator.

        :return: A position for a chair around the table.
        """

        position_to_center = table_bound_point - table_bottom
        position_to_center_normalized = position_to_center / np.linalg.norm(position_to_center)
        chair_position = table_bound_point + (position_to_center_normalized * rng.uniform(-0.125, -0.1))
        chair_position[1] = 0
        return chair_position

    def _get_plate_position(self, table_top: np.array, table_bound_point: np.array,
                            rng: np.random.RandomState) -> np.array:
        """
        :param table_top: The top of the table.
        :param table_bound_point: The bound point being used for the place setting (left, right, front, back).
        :param rng: The random number generator.

        :return: A position for a plate on the table.
        """

        # Get the vector towards the center.
        v = np.array([self.position["x"], self.position["z"]]) - np.array([table_bound_point[0], table_bound_point[2]])
        # Get the normalized direction.
        v = v / np.linalg.norm(v)
        # Move the plates inward.
        v *= float(rng.uniform(0.15, 0.2))
        # Perturb the position a bit.
        x = float(table_bound_point[0] + v[0] + rng.uniform(-0.03, 0.03))
        y = table_top[1]
        z = float(table_bound_point[2] + v[1] + rng.uniform(-0.03, 0.03))
        return np.array([x, y, z])

    @staticmethod
    def _get_fork_position(plate_position: np.array, v: np.array, rng: np.random.RandomState) -> np.array:
        """
        :param plate_position: The position of the plate.
        :param v: The forward vector.
        :param rng: The random number generator.

        :return: The fork position.
        """

        q = v * rng.uniform(0.2, 0.3)
        return np.array([plate_position[0] - q[1] + rng.uniform(-0.03, 0.03),
                         plate_position[1],
                         plate_position[2] + q[0] + rng.uniform(-0.03, 0.03)])

    @staticmethod
    def _get_knife_position(plate_position: np.array, v: np.array, rng: np.random.RandomState) -> np.array:
        """
        :param plate_position: The position of the plate.
        :param v: The forward vector.
        :param rng: The random number generator.

        :return: The knife position.
        """

        q = v * rng.uniform(0.2, 0.3)
        return np.array([plate_position[0] + q[1] + rng.uniform(-0.03, 0.03),
                         plate_position[1],
                         plate_position[2] - q[0] + rng.uniform(-0.03, 0.03)])

    @staticmethod
    def _get_spoon_position(plate_position: np.array, v: np.array, rng: np.random.RandomState) -> np.array:
        """
        :param plate_position: The position of the plate.
        :param v: The forward vector.
        :param rng: The random number generator.

        :return: The spoon position.
        """

        q = v * rng.uniform(0.3, 0.4)
        return np.array([plate_position[0] + q[1] + rng.uniform(-0.03, 0.03),
                         plate_position[1],
                         plate_position[2] - q[0] + rng.uniform(-0.03, 0.03)])

    @staticmethod
    def _get_cup_position(plate_position: np.array, v: np.array, rng: np.random.RandomState) -> np.array:
        """
        :param plate_position: The position of the plate.
        :param v: The forward vector.
        :param rng: The random number generator.

        :return: The cup position.
        """

        q = v * rng.uniform(0.2, 0.3)
        r = v * rng.uniform(0.25, 0.3)
        return np.array([plate_position[0] + q[1] + r[0] + rng.uniform(-0.03, 0.03),
                         plate_position[1],
                         plate_position[2] - q[0] + r[1] + rng.uniform(-0.03, 0.03)])
