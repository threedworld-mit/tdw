from typing import List, Tuple, Dict, Optional
import numpy as np
from tdw.controller import Controller
from tdw.proc_gen_object_recipes.proc_gen_object_recipe import ProcGenObjectRecipe
from tdw.proc_gen_object_recipes.shelf_items_type import ShelfItemsType


class Shelf(ProcGenObjectRecipe):
    """
    Add a shelf with objects on it.
    """

    """:class_var
    Shelf model names.
    """
    SHELF_MODEL_NAMES: List[str] = ["4ft_shelf_metal", "4ft_wood_shelving"]
    """:class_var
    Small items that can be placed on a shelf of random items.
    """
    SMALL_ITEMS: List[str] = ["102_pepsi_can_12_fl_oz_vray", "9v_battery", "aaa_battery", "alarm_clock",
                              "apple_ipod_touch_yellow_vray", "b03_old_scissors", "b03_padlock", "b03_pen_01_001",
                              "b03_spoon_001", "b04_cassete", "b05_48_body_shop_hair_brush", "b05_calculator",
                              "b05_champagne_cup_vray", "b05_vray_cassette_render_scene", "basic_cork", "basic_cork_2",
                              "bookend01", "bookend03", "bookend04", "bookend05", "bookend06", "bookend07",
                              "bronze_purse", "bung", "button_four_hole_large_black", "button_four_hole_large_wood",
                              "button_four_hole_mottled", "button_four_hole_red_plastic",
                              "button_four_hole_white_plastic", "button_four_hole_wood",
                              "button_two_hole_green_mottled", "button_two_hole_grey", "button_two_hole_red_mottled",
                              "button_two_hole_red_wood", "calculator", "cgaxis_models_volume_59_15_vray",
                              "champagne_cork", "coffee_cup", "coffeecup004", "cork_plastic",
                              "cork_plastic_black", "f10_apple_iphone_4", "fork1", "fork3", "fork4", "glass1", "glass2",
                              "golf", "h-shape_wood_block", "half_circle_wood_block", "holy_bible", "jug04", "jug05",
                              "key_brass", "key_dull_metal", "key_shiny", "knife1", "knife2", "l-shape_wood_block",
                              "lighter", "metal_sculpture", "mug", "notes_02", "pentagon_wood_block", "pepper",
                              "rectangle_wood_block", "remote_vr_2012", "round_coaster_cherry",
                              "round_coaster_indent_rubber", "round_coaster_indent_stone",
                              "round_coaster_indent_wood", "round_coaster_stone", "round_coaster_stone_dark",
                              "salt", "small_purse", "spoon1", "spoon2", "square_coaster_001_cork",
                              "square_coaster_001_marble", "square_coaster_001_wood", "square_coaster_rubber",
                              "square_coaster_stone", "square_coaster_wood", "square_wood_block", "star_wood_block",
                              "t-shape_wood_block", "tapered_cork", "tapered_cork_w_hole"]
    """:class_var
    The names of the baking sheet models.
    """
    BAKING_SHEETS: List[str] = ["baking_sheet01", "baking_sheet02", "baking_sheet03", "baking_sheet04",
                                "baking_sheet05", "baking_sheet06", "baking_sheet07", "baking_sheet09"]
    """:class_var
    The cell size on the "shelf grid".
    """
    CELL_SIZE: float = 0.12
    """:class_var
    Y values for each shelf.
    """
    SHELF_YS: List[float] = [0.40797001123428345, 0.8050058484077454, 1.200427532196045]
    """:class_var
    Probability of adding an item at a cell.
    """
    PROBABILITY_ITEM_AT_CELL: float = 0.66
    """:class_var
    Half of the width of the shelf.
    """
    HALF_WIDTH: float = 0.9451682 * 0.5
    """:class_var
    Half of the length of the shelf.
    """
    HALF_LENGTH: float = 0.3857702 * 0.5

    def __init__(self, position: Dict[str, float], north_south: bool, rng: np.random.RandomState = None,
                 shelf_item_type_overrides: Tuple[ShelfItemsType, ShelfItemsType, ShelfItemsType] = None):
        """
        :param position: The position of the object.
        :param north_south: If True, the object is aligned north-south (0 degree rotation). If False, the object is aligned east-west (90 degree rotation).
        :param rng: The random number generator. If None, a generator is created.
        :param shelf_item_type_overrides: If not None, a tuple of (lower, middle, upper) [shelf types](shelf_items_type.md). If None, random shelf types are chosen per shelf.
        """

        super().__init__(position=position, north_south=north_south, rng=rng)
        self._shelf_item_type_overrides: Optional[Tuple[ShelfItemsType, ShelfItemsType, ShelfItemsType]] = shelf_item_type_overrides

    def create(self) -> List[dict]:
        # Create the shelf.
        self.root_object_id = Controller.get_unique_id()
        commands = Controller.get_add_physics_object(model_name=self._rng.choice(Shelf.SHELF_MODEL_NAMES),
                                                     position=self.position,
                                                     rotation={"x": 0, "y": 90 if self.north_south else 0, "z": 0},
                                                     library="models_core.json",
                                                     object_id=self.root_object_id,
                                                     kinematic=True)
        # Manually set the types items on the shelves.
        if self._shelf_item_type_overrides is not None:
            shelf_item_types = self._shelf_item_type_overrides
        else:
            vs = [s for s in ShelfItemsType]
            shelf_item_types = (self._rng.choice(vs), self._rng.choice(vs), self._rng.choice(vs))
        for shelf_y, shelf_item_type in zip(Shelf.SHELF_YS, shelf_item_types):
            # An empty shelf.
            if shelf_item_type == ShelfItemsType.none:
                continue
            # Shelf with random items.
            elif shelf_item_type == ShelfItemsType.random:
                commands.extend(self._random_items(y=shelf_y, rng=self._rng))
            elif shelf_item_type == ShelfItemsType.baking_sheets:
                commands.extend(self._baking_sheets(y=shelf_y, rng=self._rng))
            elif shelf_item_type == ShelfItemsType.shoeboxes:
                commands.extend(self._shoeboxes(y=shelf_y, rng=self._rng))
        return commands

    def _random_items(self, y: float, rng: np.random.RandomState) -> List[dict]:
        """
        :param y: The y value of the shelf.
        :param rng: The random number generator.

        :return: A list of commands to add random small items on the shelf.
        """

        if self.north_south:
            shape = (7, 3)
        else:
            shape = (3, 7)
        commands = []
        for ix, iz in np.ndindex(shape):
            # Don't add an object.
            if rng.random() > Shelf.PROBABILITY_ITEM_AT_CELL:
                continue
            # Pick a random object.
            object_index = rng.randint(0, len(Shelf.SMALL_ITEMS))
            object_name = Shelf.SMALL_ITEMS[object_index]
            # Convert to x, z positions.
            x = (ix + 1) * Shelf.CELL_SIZE
            z = (iz + 1) * Shelf.CELL_SIZE - (Shelf.CELL_SIZE * 0.5)
            if self.north_south:
                offset_x = Shelf.HALF_WIDTH
                offset_z = Shelf.HALF_LENGTH
            else:
                offset_z = Shelf.HALF_WIDTH
                offset_x = Shelf.HALF_LENGTH
            # Add the object.
            commands.extend(Controller.get_add_physics_object(model_name=object_name,
                                                              position={"x": self.position["x"] + x - offset_x,
                                                                        "y": y,
                                                                        "z": self.position["z"] + z - offset_z},
                                                              rotation={"x": 0,
                                                                        "y": float(rng.uniform(0, 360)),
                                                                        "z": 0},
                                                              library="models_core.json",
                                                              object_id=Controller.get_unique_id()))
        return commands

    def _baking_sheets(self, y: float, rng: np.random.RandomState) -> List[dict]:
        """
        :param y: The y value of the shelf.
        :param rng: The random number generator.

        :return: A list of commands to add baking sheets to the shelf.
        """

        commands = []
        i = float(rng.uniform(-Shelf.HALF_LENGTH, Shelf.HALF_LENGTH)) * 0.25
        j = float(rng.uniform(-Shelf.HALF_WIDTH, Shelf.HALF_WIDTH)) * 0.25
        if self.north_south:
            x = self.position["x"] + j
            z = self.position["z"] + i
        else:
            x = self.position["x"] + i
            z = self.position["z"] + j
        # Add random baking sheets.
        sheet_y = y
        for i in range(rng.randint(4, 8)):
            sheet_name: str = rng.choice(Shelf.BAKING_SHEETS)
            commands.extend(Controller.get_add_physics_object(model_name=sheet_name,
                                                              object_id=Controller.get_unique_id(),
                                                              position={"x": x, "y": sheet_y, "z": z},
                                                              rotation={"x": 0,
                                                                        "y": float(rng.uniform(-90, 90)),
                                                                        "z": 0},
                                                              library="models_core.json"))
            # Place the next sheet on top of this one.
            sheet_record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(sheet_name)
            sheet_y += np.linalg.norm(sheet_record.bounds["top"]["y"] - sheet_record.bounds["bottom"]["y"])
        return commands

    def _shoeboxes(self, y: float, rng: np.random.RandomState) -> List[dict]:
        """
        :param y: The y value of the shelf.
        :param rng: The random number generator.

        :return: A list of commands to add shoeboxes to the shelf.
        """

        shoebox_layout_variants = [[True, True], [True, False], [False, True]]
        shoebox_variant_index = rng.randint(0, 2)
        commands = []
        for shoebox, direction in zip(shoebox_layout_variants[shoebox_variant_index], [-1, 1]):
            if not shoebox:
                continue
            i = (0.214 * direction) + float(rng.uniform(-0.03, 0.03))
            j = float(rng.uniform(-0.1, 0.1))
            if self.north_south:
                rotation = 0
                x = self.position["x"] + i
                z = self.position["z"] + j
            else:
                rotation = 90
                x = self.position["x"] + j
                z = self.position["z"] + i
            rotation += float(rng.uniform(-30, 30))
            commands.extend(Controller.get_add_physics_object(model_name="shoebox_fused",
                                                              position={"x": x, "y": y, "z": z},
                                                              rotation={"x": 0, "y": rotation, "z": 0},
                                                              object_id=Controller.get_unique_id()))
        return commands
