# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.create_reverb_space_command import CreateReverbSpaceCommand


class SetReverbSpaceSimple(CreateReverbSpaceCommand):
    """
    Create a ResonanceAudio Room, sized to the dimensions of the current room environment. Reflectivity (early reflections) and reverb brightness (late reflections) calculated automatically based on size of space and percentage filled with objects.
    """

    def __init__(self, min_room_volume: float = 27.0, max_room_volume: float = 1000.0, region_id: int = -1, reverb_floor_material: str = "parquet", reverb_ceiling_material: str = "acousticTile", reverb_front_wall_material: str = "smoothPlaster", reverb_back_wall_material: str = "smoothPlaster", reverb_left_wall_material: str = "smoothPlaster", reverb_right_wall_material: str = "smoothPlaster"):
        """
        :param min_room_volume: Minimum possible volume of a room (i.e. 1 x 1 x 1 room).
        :param max_room_volume: Maximum room volume. This is purely for range-setting for reflectivity calculation.
        :param region_id: The ID of the scene region (room) to enable reverberation in. If -1, the reverb space will encapsulate the entire scene instead of a single room.
        :param reverb_floor_material: The surface material of the reverb space floor.
        :param reverb_ceiling_material: The surface material of the reverb space ceiling.
        :param reverb_front_wall_material: The surface material of the reverb space front wall.
        :param reverb_back_wall_material: The surface material of the reverb space back wall.
        :param reverb_left_wall_material: The surface material of the reverb space left wall.
        :param reverb_right_wall_material: The surface material of the reverb space right wall.
        """

        super().__init__(region_id=region_id, reverb_floor_material=reverb_floor_material, reverb_ceiling_material=reverb_ceiling_material, reverb_front_wall_material=reverb_front_wall_material, reverb_back_wall_material=reverb_back_wall_material, reverb_left_wall_material=reverb_left_wall_material, reverb_right_wall_material=reverb_right_wall_material)
        """:field
        Minimum possible volume of a room (i.e. 1 x 1 x 1 room).
        """
        self.min_room_volume: float = min_room_volume
        """:field
        Maximum room volume. This is purely for range-setting for reflectivity calculation.
        """
        self.max_room_volume: float = max_room_volume
