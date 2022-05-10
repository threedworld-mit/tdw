from typing import Dict
from pkg_resources import resource_filename
from json import loads
from pathlib import Path


class SoftBodyMaterial:
    """
    An Obi softbody material. For more information, [read this](http://obi.virtualmethodstudio.com/tutorials/clothsetup.html).
    """

    def __init__(self, visual_material: str, texture_scale: Dict[str, float], visual_smoothness: float = 0,
                 deformation_resistance: float = 1.0, max_deformation: float = 0, plastic_yield: float = 0,
                 plastic_creep: float = 0, plastic_recovery: float = 0, surface_sampling_resolution: int = 16, shape_analysis_resolution: int = 48,
                 shape_analysis_smoothing: float = 0.25):
        """
        :param visual_material: The name of the visual material associated with this cloth material.
        :param texture_scale: The texture scale of the visual material.
        :param visual_smoothness: The smoothness value of the visual material.
        :param deformation_resistance: The scale factor for the rest length of each constraint.
        :param max_deformation: Controls how much constraints will resist a change in length.
        :param plastic_yield: The percentage of compression allowed by the constraints before kicking in.
        :param plastic_creep: The amount of bending allowed before the constraints kick in, expressed in world units.
        :param plastic_recovery: Controls how much constraints will resist a change in curvature, once they are past the maximum bending threshold.
        :param surface_sampling_resolution: How much drag affects the cloth. The value is multiplied by the air density value.
        :param shape_analysis_resolution: How much lift affects the cloth. The value is multiplied by the air density value
        :param shape_analysis_smoothing: How much lift affects the cloth. The value is multiplied by the air density value
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
        How strongly will particle clusters resist deviation from their rest shape.
        """
        self.deformation_resistance: float = deformation_resistance
        """:field
        The maximum value of the deformation.
        """
        self.max_deformation: float = max_deformation
        """:field
        Strain threshold that marks the transition from elastic to plastic deformation.
        """
        self.plastic_yield: float = plastic_yield
        """:field
        Determines what percentage of the deformation is permanently absorbed by the cluster.
        """
        self.plastic_creep: float = plastic_creep
        """:field
        Speed at which clusters recover from plastic deformation, in % per second.
        """
        self.plastic_recovery: float = plastic_recovery
        """:field
        How fine grained particle sampling will be, across the surface of the mesh.
        """
        self.surface_sampling_resolution: float = surface_sampling_resolution
        """:field
        How fine voxelization will be, in the shape analysis stage.
        """
        self.shape_analysis_resolution: float = shape_analysis_resolution
        """:field
        Amount of laplacian smoothing applied to particles.
        """
        self.shape_analysis_smoothing: float = shape_analysis_smoothing


    def to_dict(self) -> dict:
        """
        :return: A JSON dictionary of this object.
        """

        d = {"$type": "softbody_material"}
        d.update(self.__dict__)
        return d


def __get() -> Dict[str, SoftBodyMaterial]:
    data = loads(Path(resource_filename(__name__, "data/cloth_materials.json")).read_text())
    materials = dict()
    for k in data:
        materials[k] = SoftBodyMaterial(**data[k])
    return materials


SOFTBODY_MATERIALS: Dict[str, SoftBodyMaterial] = __get()
