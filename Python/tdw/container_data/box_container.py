from typing import Dict
from tdw.container_data.container_shape import ContainerShape
from tdw.container_data.container_tag import ContainerTag


class BoxContainer(ContainerShape):
    """
    A box-shaped container shape.
    """

    def __init__(self, tag: ContainerTag, position: Dict[str, float], half_extents: Dict[str, float], rotation: Dict[str, float]):
        """
        :param tag: The box's semantic [`ContainerTag`](container_tag.md).
        :param position: The position of the box relative to the parent object.
        :param half_extents: The half extents of the box.
        :param rotation: The rotation of the box relative to the parent object in Euler angles.
        """

        super().__init__(tag=tag, position=position)
        """:field
        The half extents of the box.
        """
        self.half_extents: Dict[str, float] = {k: float(v) for k, v in half_extents.items()}
        """:field
        The rotation of the box relative to the parent object in Euler angles.
        """
        self.rotation: Dict[str, float] = {k: float(v) for k, v in rotation.items()}
