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
        :param deformation_resistance: How strongly will particle clusters resist deviation from their rest shape.
        :param max_deformation: The maximum value of the deformation.
        :param plastic_yield: Strain threshold that marks the transition from elastic to plastic deformation.
        :param plastic_creep: Determines what percentage of the deformation is permanently absorbed by the cluster.
        :param plastic_recovery: Speed at which clusters recover from plastic deformation, in % per second.
        :param surface_sampling_resolution: How fine grained particle sampling will be, across the surface of the mesh.
        :param shape_analysis_resolution:  How fine voxelization will be, in the shape analysis stage.
        :param shape_analysis_smoothing: Amount of laplacian smoothing applied to particles.
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
    data = loads(Path(resource_filename(__name__, "data/softbody_materials.json")).read_text())
    materials = dict()
    for k in data:
        materials[k] = SoftBodyMaterial(**data[k])
    return materials


SOFTBODY_MATERIALS: Dict[str, SoftBodyMaterial] = __get()
