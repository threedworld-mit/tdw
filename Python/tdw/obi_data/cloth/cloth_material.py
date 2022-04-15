from typing import Dict
from pkg_resources import resource_filename
from json import loads
from pathlib import Path


class ClothMaterial:
    """
    An Obi cloth material.
    """

    def __init__(self, visual_material: str, texture_scale: Dict[str, float], stretching_scale: float = 1.0,
                 stretch_compliance: float = 0, max_compression: float = 0, max_bending: float = 0.05,
                 bend_compliance: float = 0, drag: float = 0.05, lift: float = 0.05, tether_compliance: float = 0,
                 tether_scale: float = 1.0):
        """
        :param visual_material: The name of the visual material associated with this cloth material.
        :param texture_scale: The texture scale of the visual material.
        :param stretching_scale: The scale factor for the rest length of each constraint.
        :param stretch_compliance: Controls how much constraints will resist a change in length.
        :param max_compression: The percentage of compression allowed by the constraints before kicking in. 
        :param max_bending: The amount of bending allowed before the constraints kick in, expressed in world units.
        :param bend_compliance: Controls how much constraints will resist a change in curvature, once they are past the maximum bending threshold.
        :param drag: How much drag affects the cloth. The value is multiplied by the air density value.
        :param lift: How much lift affects the cloth. The value is multiplied by the air density value.
        :param tether_compliance: Controls how much constraints will resist stretching
        :param tether_scale: Scales the initial length of tethers.
        """

        """:field
        The name of the visual material associated with this cloth material.
        """
        self.visual_material: str = visual_material
        """:field
        The texture scale of the visual material.
        """
        self.texture_scale: Dict[str, float] = texture_scale
        """:field
        The scale factor for the rest length of each constraint.
        """
        self.stretching_scale: float = stretching_scale    
        """:field
        Controls how much constraints will resist a change in length.
        """
        self.stretch_compliance: float = stretch_compliance
        """:field
        The percentage of compression allowed by the constraints before kicking in.
        """
        self.max_compression: float = max_compression
        """:field
        The amount of bending allowed before the constraints kick in, expressed in world units.
        """
        self.max_bending: float = max_bending
        """:field
        Controls how much constraints will resist a change in curvature, once they are past the maximum bending threshold.
        """
        self.bend_compliance: float = bend_compliance
        """:field
        How much drag affects the cloth. The value is multiplied by the air density value.
        """
        self.drag: float = drag
        """:field
        How much lift affects the cloth. The value is multiplied by the air density value.
        """
        self.lift: float = lift
        """:field
        Controls how much constraints will resist stretching
        """
        self.tether_compliance: float = tether_compliance
        """:field
        Scales the initial length of tethers.
        """
        self.tether_scale: float = tether_scale

    def to_dict(self) -> dict:
        """
        :return: A JSON dictionary of this object.
        """

        d = {"$type": "cloth_material"}
        d.update(self.__dict__)
        return d


def __get() -> Dict[str, ClothMaterial]:
    data = loads(Path(resource_filename(__name__, "data/cloth_materials.json")).read_text())
    materials = dict()
    for k in data:
        materials[k] = ClothMaterial(**data[k])
    return materials


CLOTH_MATERIALS: Dict[str, ClothMaterial] = __get()
