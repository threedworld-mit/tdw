# AUTOGENERATED FROM C#. DO NOT MODIFY.

from abc import ABC
from tdw.commands.command import Command


class CreateReverbSpaceCommand(Command, ABC):
    """
    Base class to create a ResonanceAudio Room, sized to the dimensions of the current room environment.
    """

    def __init__(self, region_id: int = -1, reverb_floor_material: str = "parquet", reverb_ceiling_material: str = "acousticTile", reverb_front_wall_material: str = "smoothPlaster", reverb_back_wall_material: str = "smoothPlaster", reverb_left_wall_material: str = "smoothPlaster", reverb_right_wall_material: str = "smoothPlaster"):
        """
        :param region_id: The ID of the scene region (room) to enable reverberation in. If -1, the reverb space will encapsulate the entire scene instead of a single room.
        :param reverb_floor_material: The surface material of the reverb space floor.
        :param reverb_ceiling_material: The surface material of the reverb space ceiling.
        :param reverb_front_wall_material: The surface material of the reverb space front wall.
        :param reverb_back_wall_material: The surface material of the reverb space back wall.
        :param reverb_left_wall_material: The surface material of the reverb space left wall.
        :param reverb_right_wall_material: The surface material of the reverb space right wall.
        """

        super().__init__()
        """:field
        The ID of the scene region (room) to enable reverberation in. If -1, the reverb space will encapsulate the entire scene instead of a single room.
        """
        self.region_id: int = region_id
        """:field
        The surface material of the reverb space floor.
        """
        self.reverb_floor_material: str = reverb_floor_material
        """:field
        The surface material of the reverb space ceiling.
        """
        self.reverb_ceiling_material: str = reverb_ceiling_material
        """:field
        The surface material of the reverb space front wall.
        """
        self.reverb_front_wall_material: str = reverb_front_wall_material
        """:field
        The surface material of the reverb space back wall.
        """
        self.reverb_back_wall_material: str = reverb_back_wall_material
        """:field
        The surface material of the reverb space left wall.
        """
        self.reverb_left_wall_material: str = reverb_left_wall_material
        """:field
        The surface material of the reverb space right wall.
        """
        self.reverb_right_wall_material: str = reverb_right_wall_material