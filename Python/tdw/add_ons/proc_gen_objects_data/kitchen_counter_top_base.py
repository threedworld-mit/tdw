from abc import ABC, abstractmethod
from typing import Dict, List, Tuple
import numpy as np
from tdw.controller import Controller
from tdw.add_ons.proc_gen_objects_data.arrangement_along_wall import ArrangementAlongWall
from tdw.scene_data.interior_region import InteriorRegion
from tdw.cardinal_direction import CardinalDirection
from tdw.librarian import ModelRecord


class KitchenCounterTopBase(ArrangementAlongWall, ABC):
    """
    Abstract base class for arrangments that including a floating kitchen counter top.
    """

    def __init__(self, material: str, wall: CardinalDirection, region: InteriorRegion, record: ModelRecord,
                 position: Dict[str, float], rng: np.random.RandomState):
        """
        :param material: The name of the visual material.
        :param wall: The wall as a [`CardinalDirection`](../../cardinal_direction.md) that the root object is next to.
        :param region: The [`InteriorRegion`](../../scene_data/interior_region.md) that the object is in.
        :param record: The model record.
        :param position: The position of the root object. This might be adjusted.
        :param rng: The random number generator.
        """

        super().__init__(wall=wall, region=region, record=record, position=position, rng=rng)
        self._material: str = material
        self._size: Tuple[float, float] = self._get_size()

    def get_commands(self) -> List[dict]:
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
