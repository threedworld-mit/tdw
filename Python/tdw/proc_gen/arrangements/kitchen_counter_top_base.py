from abc import ABC, abstractmethod
from typing import List, Tuple, Union
import numpy as np
from overrides import final
from tdw.controller import Controller
from tdw.proc_gen.arrangements.arrangement_along_wall import ArrangementAlongWall
from tdw.scene_data.interior_region import InteriorRegion
from tdw.librarian import ModelRecord
from tdw.cardinal_direction import CardinalDirection
from tdw.ordinal_direction import OrdinalDirection
from tdw.proc_gen.arrangements.kitchen_cabinets.kitchen_cabinet_set import KitchenCabinetSet


class KitchenCounterTopBase(ArrangementAlongWall, ABC):
    """
    Abstract base class for arrangements that including a floating kitchen counter top.
    """

    def __init__(self, cabinetry: KitchenCabinetSet, corner: OrdinalDirection, wall: CardinalDirection, distance: float,
                 region: InteriorRegion, model: Union[str, ModelRecord] = None, wall_length: float = None,
                 rng: np.random.RandomState = None):
        """
        :param cabinetry: The [`KitchenCabinetSet`](kitchen_cabinets/kitchen_cabinet_set.md).
        :param wall: The wall as a [`CardinalDirection`](../../cardinal_direction.md) that the root object is next to.
        :param corner: The origin [`Corner`](../../corner.md) of this wall. This is used to derive the direction.
        :param distance: The distance in meters from the corner along the derived direction.
        :param region: The [`InteriorRegion`](../../scene_data/interior_region.md) that the object is in.
        :param model: Either the name of the model (in which case the model must be in `models_core.json`), or a `ModelRecord`, or None. If None, a model that fits along the wall at `distance` is randomly selected. If no model fits, the arrangement will not be added to the scene.
        :param wall_length: The total length of the lateral arrangement. If None, defaults to the length of the wall.
        :param rng: The random number generator. If None, a new random number generator is created.
        """

        self._material: str = cabinetry.counter_top_material
        super().__init__(corner=corner, wall=wall, distance=distance, region=region, model=model,
                         wall_length=wall_length, rng=rng)
        self._size: Tuple[float, float] = self._get_size()

    @final
    def _add_kitchen_counter_top(self) -> List[dict]:
        scale_factor = {"x": self._size[0], "y": 0.0371, "z": self._size[1]}
        if self._wall == CardinalDirection.west or self._wall == CardinalDirection.east:
            rotation = 90
        else:
            rotation = 0
        object_id = Controller.get_unique_id()
        commands = [{"$type": "load_primitive_from_resources",
                     "primitive_type": "Cube",
                     "id": object_id,
                     "position": {"x": self._position["x"], "y": 0.9, "z": self._position["z"]},
                     "orientation": {"x": 0, "y": rotation, "z": 0}},
                    Controller.get_add_material(self._material, "materials_med.json"),
                    {"$type": "set_primitive_visual_material",
                     "name": self._material,
                     "id": object_id},
                    {"$type": "scale_object",
                     "id": object_id,
                     "scale_factor": scale_factor},
                    {"$type": "set_kinematic_state",
                     "id": object_id,
                     "is_kinematic": True}]
        # Add objects on top of the counter.
        object_commands, object_ids = self._add_rectangular_arrangement(size=(scale_factor["x"] * 0.8, scale_factor["z"] * 0.8),
                                                                        position={"x": self._position["x"],
                                                                                  "y": 0.9167836,
                                                                                  "z": self._position["z"]},
                                                                        categories=ArrangementAlongWall.ON_TOP_OF["kitchen_counter"])
        self.object_ids.append(object_id)
        self.object_ids.extend(object_ids)
        commands.extend(object_commands)
        return commands

    @abstractmethod
    def _get_size(self) -> Tuple[float, float]:
        """
        :return: The (x, z) size of the counter top.
        """

        raise Exception()
