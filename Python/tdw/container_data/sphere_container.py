from typing import Dict
from tdw.container_data.container_shape import ContainerShape
from tdw.container_data.container_tag import ContainerTag


class SphereContainer(ContainerShape):
    """
    A spherical container shape.
    """

    def __init__(self, tag: ContainerTag, position: Dict[str, float], radius: float):
        """
        :param tag: The sphere's semantic [`ContainerTag`](container_tag.md).
        :param position: The position of the sphere relative to the parent object.
        :param radius: The radius of the sphere.
        """

        super().__init__(tag=tag, position=position)
        """:field
        The radius of the sphere.
        """
        self.radius: float = radius
