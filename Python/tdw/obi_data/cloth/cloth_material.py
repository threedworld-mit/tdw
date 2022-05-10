from typing import Dict
from pkg_resources import resource_filename
from json import loads
from pathlib import Path


class ClothMaterial:
    """
    An Obi cloth material. For more information, [read this](http://obi.virtualmethodstudio.com/tutorials/clothsetup.html).
    """

    def __init__(self, visual_material: str, texture_scale: Dict[str, float], visual_smoothness: float = 0,
                 stretching_scale: float = 1.0, stretch_compliance: float = 0, max_compression: float = 0,
                 max_bending: float = 0.05, bend_compliance: float = 0, drag: float = 0.05, lift: float = 0.05,
                 mass_per_square_meter: float = 1):
        """
        :param visual_material: The name of the visual material associated with this cloth material.
        :param texture_scale: The texture scale of the visual material.
        :param visual_smoothness: The smoothness value of the visual material.
        :param stretching_scale: The scale factor for the rest length of each constraint.
        :param stretch_compliance: Controls how much constraints will resist a change in length.
        :param max_compression: The percentage of compression allowed by the constraints before kicking in. 
        :param max_bending: The amount of bending allowed before the constraints kick in, expressed in world units.
        :param bend_compliance: Controls how much constraints will resist a change in curvature, once they are past the maximum bending threshold.
        :param drag: How much drag affects the cloth. The value is multiplied by the air density value.
        :param lift: How much lift affects the cloth. The value is multiplied by the air density value.
        :param mass_per_square_meter: The mass in kg per square meter of cloth surface area.
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
        The smoothness value of the visual material.
        """
        self.visual_smoothness: float = visual_smoothness
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
        The mass in kg per square meter of cloth surface area.
        """
        self.mass_per_square_meter: float = mass_per_square_meter

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
