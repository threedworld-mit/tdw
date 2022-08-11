from pkg_resources import resource_filename
from json import loads
from pathlib import Path
from typing import List, Dict
from tdw.add_ons.audio_initializer_base import AudioInitializerBase
from tdw.physics_audio.audio_material import AudioMaterial


class ResonanceAudioInitializer(AudioInitializerBase):
    """
    Initialize Resonance Audio.

    This assumes that an avatar corresponding to `avatar_id` has already been added to the scene.
    """

    """:class_var
    A dictionary. Key = A Resonance Audio material string. Value = An [`AudioMaterial`](../physics_audio/audio_material.md).
    """
    AUDIO_MATERIALS: Dict[str, AudioMaterial] = {k: AudioMaterial[v] for k, v in loads(Path(resource_filename(__name__, "../physics_audio/resonance_audio_materials.json")).read_text()).items()}

    def __init__(self, avatar_id: str = "a", region_id: int = -1, floor: str = "parquet", ceiling: str = "acousticTile",
                 front_wall: str = "smoothPlaster", back_wall: str = "smoothPlaster", left_wall: str = "smoothPlaster",
                 right_wall: str = "smoothPlaster", framerate: int = 60):
        """
        :param avatar_id: The ID of the avatar.
        :param region_id: The ID of the scene region (room) to enable reverberation in. If -1, the reverb space will encapsulate the entire scene instead of a single room.
        :param floor: The floor material. [Read this for a list of options.](../../api/command_api.md#set_reverb_space_simple)
        :param ceiling: The ceiling material. [Read this for a list of options.](../../api/command_api.md#set_reverb_space_simple)
        :param front_wall: The front wall material. [Read this for a list of options.](../../api/command_api.md#set_reverb_space_simple)
        :param back_wall: The back wall material. [Read this for a list of options.](../../api/command_api.md#set_reverb_space_simple)
        :param left_wall: The left wall material. [Read this for a list of options.](../../api/command_api.md#set_reverb_space_simple)
        :param right_wall: The right wall material. [Read this for a list of options.](../../api/command_api.md#set_reverb_space_simple)
        :param framerate: The target simulation framerate.
        """

        super().__init__(avatar_id=avatar_id, framerate=framerate)
        """:field
        The ID of the scene region (room) to enable reverberation in. If -1, the reverb space will encapsulate the entire scene instead of a single room.
        """
        self.region_id = region_id
        """:field
        The floor material. [Read this for a list of options.](../../api/command_api.md#set_reverb_space_simple)
        """
        self.floor: str = floor
        """:field
        The ceiling material. [Read this for a list of options.](../../api/command_api.md#set_reverb_space_simple)
        """
        self.ceiling: str = ceiling
        """:field
        The front wall material. [Read this for a list of options.](../../api/command_api.md#set_reverb_space_simple)
        """
        self.front_wall: str = front_wall
        """:field
        The back wall material. [Read this for a list of options.](../../api/command_api.md#set_reverb_space_simple)
        """
        self.back_wall: str = back_wall
        """:field
        The left wall material. [Read this for a list of options.](../../api/command_api.md#set_reverb_space_simple)
        """
        self.left_wall: str = left_wall
        """:field
        The right wall material. [Read this for a list of options.](../../api/command_api.md#set_reverb_space_simple)
        """
        self.right_wall: str = right_wall

    def get_initialization_commands(self) -> List[dict]:
        commands = super().get_initialization_commands()
        commands.insert(0, {"$type": "set_reverb_space_simple",
                            "region_id": self.region_id,
                            "reverb_floor_material": self.floor,
                            "reverb_ceiling_material": self.ceiling,
                            "reverb_front_wall_material": self.front_wall,
                            "reverb_back_wall_material": self.back_wall,
                            "reverb_left_wall_material": self.left_wall,
                            "reverb_right_wall_material": self.right_wall})
        return commands

    def _get_sensor_command_name(self) -> str:
        return "add_environ_audio_sensor"

    def _get_play_audio_command_name(self) -> str:
        return "play_point_source_data"
