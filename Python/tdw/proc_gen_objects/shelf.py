from typing import List, Dict, Tuple
from pkg_resources import resource_filename
from pathlib import Path
from json import loads
import numpy as np
from tdw.controller import Controller
from tdw.proc_gen_objects.proc_gen_object import ProcGenObject


class Shelf(ProcGenObject):
    """
    Add a shelf with objects on it.
    """

    """:class_var
    Pre-calculated dimensions of objects from the core model library where each unit is a "cell" of a shelf grid.
    """
    ITEMS: Dict[str, Tuple[int, int]] = {k: (v[0], v[1]) for k, v in
                                         loads(Path(resource_filename(__name__, "shelf_items.json")).read_text()).items()}
    ITEMS_LIST: List[str] = list(ITEMS.keys())
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

    def create(self, rng: np.random.RandomState) -> List[dict]:
        # Create the shelf.
        commands = Controller.get_add_physics_object(model_name="4ft_shelf_metal",
                                                     position=self.position,
                                                     rotation={"x": 0, "y": 90 if self.north_south else 0, "z": 0},
                                                     library="models_core.json",
                                                     object_id=Controller.get_unique_id(),
                                                     kinematic=True)
        for shelf_y in Shelf.SHELF_YS:
            if self.north_south:
                shelf = np.zeros(shape=(7, 3), dtype=bool)
            else:
                shelf = np.zeros(shape=(3, 7), dtype=bool)
            for ix, iz in np.ndindex(shelf.shape):
                if shelf[ix][iz] or rng.random() > Shelf.PROBABILITY_ITEM_AT_CELL:
                    continue
                # Pick a random object.
                object_index = rng.randint(0, len(Shelf.ITEMS_LIST))
                object_name = Shelf.ITEMS_LIST[object_index]
                if ix + Shelf.ITEMS[object_name][0] > shelf.shape[0] or iz + Shelf.ITEMS[object_name][1] > shelf.shape[1]:
                    continue
                # Convert to x, z positions.
                x = (ix + Shelf.ITEMS[object_name][0] / 2) * Shelf.CELL_SIZE
                z = (iz + Shelf.ITEMS[object_name][1] / 2) * Shelf.CELL_SIZE
                if self.north_south:
                    offset_x = Shelf.HALF_WIDTH
                    offset_z = Shelf.HALF_LENGTH
                else:
                    offset_z = Shelf.HALF_WIDTH
                    offset_x = Shelf.HALF_LENGTH
                # Add the object.
                commands.extend(Controller.get_add_physics_object(model_name=object_name,
                                                                  position={"x": self.position["x"] + x - offset_x,
                                                                            "y": shelf_y,
                                                                            "z": self.position["z"] + z - offset_z},
                                                                  rotation={"x": 0,
                                                                            "y": float(rng.uniform(-15, 15)) + (0 if self.north_south else 90),
                                                                            "z": 0},
                                                                  library="models_core.json",
                                                                  object_id=Controller.get_unique_id()))
                # Mark these grid cells as filled.
                for iix, iiz in np.ndindex(Shelf.ITEMS[object_name]):
                    shelf[ix + iix][iz + iiz] = True
        return commands

s = Shelf(position={"x": 1, "y": 0, "z": 2}, north_south=False)
from tdw.tdw_utils import TDWUtils

c = Controller()
cmds = [TDWUtils.create_empty_room(12, 12)]
cmds.extend(s.create(np.random.RandomState()))
c.communicate(cmds)