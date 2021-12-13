from typing import List, Tuple, Dict
import numpy as np
from tdw.librarian import ModelLibrarian
from tdw.proc_gen_object_recipes.proc_gen_object_recipe import ProcGenObjectRecipe
from tdw.cardinal_direction import CardinalDirection
from tdw.controller import Controller


class KitchenCounter(ProcGenObjectRecipe):
    _WOOD_TYPES: List[str] = ["white_wood", "wood_beach_honey"]
    _CABINET_DEPTH: float = 0.6424497
    _CABINET_36_LENGTH: float = 0.9098791
    _CABINET_24_LENGTH: float = 0.6073107
    _WALL_DEPTH: float = 0.28

    def __init__(self, wall: CardinalDirection, room_size: Tuple[float, float], rng: np.random.RandomState = None):
        if wall == CardinalDirection.north:
            north_south = False
            position = {"x": 0,
                        "y": 0,
                        "z": room_size[1] / 2 - (KitchenCounter._CABINET_DEPTH + KitchenCounter._WALL_DEPTH)}
            self._rotation: int = 0
        elif wall == CardinalDirection.south:
            north_south = False
            position = {"x": 0,
                        "y": 0,
                        "z": -room_size[1] / 2 + (KitchenCounter._CABINET_DEPTH + KitchenCounter._WALL_DEPTH)}
            self._rotation = 180
        elif wall == CardinalDirection.west:
            north_south = True
            position = {"x": room_size[0] / 2 - (KitchenCounter._CABINET_DEPTH + KitchenCounter._WALL_DEPTH),
                        "y": 0,
                        "z": 0}
            self._rotation = 90
        elif wall == CardinalDirection.east:
            north_south = True
            position = {"x": -room_size[0] / 2 + (KitchenCounter._CABINET_DEPTH + KitchenCounter._WALL_DEPTH),
                        "y": 0,
                        "z": 0}
            self._rotation = 270
        else:
            raise Exception(wall)
        super().__init__(position=position, north_south=north_south, rng=rng)
        self._wall: CardinalDirection = wall
        self._room_size: Tuple[float, float] = room_size

    def create(self) -> List[dict]:
        wood_type = self._rng.choice(KitchenCounter._WOOD_TYPES)
        cabinet_24 = f"cabinet_24_{wood_type}"
        cabinet_36 = f"cabinet_36_{wood_type}"
        commands = Controller.get_add_physics_object(model_name=cabinet_36,
                                                     library="models_core.json",
                                                     position=self.position,
                                                     rotation={"x": 0, "y": self._rotation, "z": 0},
                                                     object_id=Controller.get_unique_id(),
                                                     kinematic=True)
        x = KitchenCounter._CABINET_36_LENGTH
        while x < self._room_size[0] / 2 - (KitchenCounter._WALL_DEPTH + KitchenCounter._CABINET_36_LENGTH):
            commands.extend(Controller.get_add_physics_object(model_name=cabinet_36,
                                                              library="models_core.json",
                                                              position={"x": x,
                                                                        "y": 0,
                                                                        "z": self._room_size[1] / 2 - (
                                                                                    KitchenCounter._CABINET_DEPTH + KitchenCounter._WALL_DEPTH)},
                                                              rotation={"x": 0, "y": self._rotation, "z": 0},
                                                              object_id=Controller.get_unique_id(),
                                                              kinematic=True))
            x += KitchenCounter._CABINET_36_LENGTH
        return commands



from tdw.tdw_utils import TDWUtils
c = Controller()
kc = KitchenCounter(room_size=(8, 4), wall=CardinalDirection.north)
commands = [TDWUtils.create_empty_room(8, 4)]
commands.extend(kc.create())
c.communicate(commands)