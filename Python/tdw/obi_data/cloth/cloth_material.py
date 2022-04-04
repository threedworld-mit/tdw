from pkg_resources import resource_filename
from pathlib import Path
from json import loads
from typing import Dict
from tdw.obi_data.cloth.cloth_material_base import ClothMaterialBase


class ClothMaterial(ClothMaterialBase):
    """
    Data for an Obi cloth material. For more information, [read this](http://obi.virtualmethodstudio.com/tutorials/emittermaterials.html).
    """

    def __init__(self, 
                 distance_constraints_enabled: bool, bend_constraints_enabled: bool,  
                 aerodynamics_constraints_enabled: bool, tether_constraints_enabled: bool, 
                 stretching_scale: float = 1.0, stretch_compliance: float = 0, max_compression: float = 0,
                 max_bending: float = 0.05, bend_compliance: float = 0, drag: float = 0.05, lift: float = 0.05,
                 tether_compliance: float = 0, tether_scale: float = 1.0
                ):
        """
        :param distance_constraints_enabled: Are distance constraints enabled?
        :param bend_constraints_enabled: Are bend constraints enabled?
        :param aerodynamics_constraints_enabled: Are aerodynamics constraints enabled?
        :param tether_constraints_enabled: Are tether constraints enabled?
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

        super().__init__(distance_constraints_enabled=distance_constraints_enabled, bend_constraints_enabled=bend_constraints_enabled, 
                         aerodynamics_constraints_enabled=aerodynamics_constraints_enabled, tether_constraints_enabled=tether_constraints_enabled,
                         stretching_scale=stretching_scale, stretch_compliance=stretch_compliance, max_compression=max_compression, 
                         max_bending=max_bending, bend_compliance=bend_compliance, drag=drag, lift=lift,
                         tether_compliance=tether_compliance, tether_scale=tether_scale)


    def _get_type(self) -> str:
        return "fluid"


def __get() -> Dict[str, ClothMaterial]:
    data = loads(Path(resource_filename(__name__, "data/cloth_materials.json")).read_text())
    materials = dict()
    for k in data:
        materials[k] = ClothMaterial(**data[k])
    return materials


CLOTHMATERIALS: Dict[str, ClothMaterial] = __get()
