# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.add_container_shape_command import AddContainerShapeCommand
from tdw.container_data.container_tag import ContainerTag
from typing import Dict


class AddBoxContainer(AddContainerShapeCommand):
    """
    Add a box container shape to an object. The object will send output data whenever other objects overlap with this volume.
    """

    def __init__(self, id: int, tag: ContainerTag, half_extents: Dict[str, float] = None, rotation: Dict[str, float] = None, container_id: int = 0, position: Dict[str, float] = None):
        """
        :param id: The unique object ID.
        :param tag: The container tag.
        :param half_extents: The half extents of the box.
        :param rotation: The rotation of the box in Euler angles relative to the parent object.
        :param container_id: The ID of this container shape. This can be used to differentiate between multiple container shapes belonging to the same object.
        :param position: The position of the container shape relative to the parent object.
        """

        super().__init__(container_id=container_id, position=position, tag=tag, id=id)
        if half_extents is None:
            """:field
            The half extents of the box.
            """
            self.half_extents: Dict[str, float] = {"x": 1, "y": 1, "z": 1}
        else:
            self.half_extents = half_extents
        if rotation is None:
            """:field
            The rotation of the box in Euler angles relative to the parent object.
            """
            self.rotation: Dict[str, float] = {"x": 0, "y": 0, "z": 0}
        else:
            self.rotation = rotation
