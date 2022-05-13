from typing import Dict
from tdw.container_data.container_shape import ContainerShape
from tdw.container_data.container_tag import ContainerTag


class CylinderContainer(ContainerShape):
    """
    A cylindrical container shape.
    """

    def __init__(self, tag: ContainerTag, position: Dict[str, float], radius: float, height: float, rotation: Dict[str, float]):
        """
        :param tag: The cylinder's semantic [`ContainerTag`](container_tag.md).
        :param position: The position of the cylinder relative to the parent object.
        :param radius: The radius of the cylinder.
        :param height: The height of the cylinder.
        :param rotation: The rotation of the cylinder relative to the parent object in Euler angles.
        """

        super().__init__(tag=tag, position=position)
        """:field
        The radius of the cylinder.
        """
        self.radius: float = radius
        """:field
        The height of the cylinder.
        """
        self.height: float = height
        """:field
        The rotation of the cylinder relative to the parent object in Euler angles.
        """
        self.rotation: Dict[str, float] = rotation
