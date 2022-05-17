from typing import List, Dict
from tdw.add_ons.third_person_camera_base import ThirdPersonCameraBase
from tdw.output_data import OutputData, Mouse, Raycast, Keyboard
from tdw.tdw_utils import TDWUtils


class FirstPersonCamera(ThirdPersonCameraBase):
    MOUSE_RAYCAST_ID: int = 1234567

    def __init__(self, avatar_id: str = None, position: Dict[str, float] = None, rotation: Dict[str, float] = None,
                 field_of_view: int = None):
        super().__init__(avatar_id=avatar_id, position=position, rotation=rotation, field_of_view=field_of_view)
        self.is_object_at_cursor: bool = False
        self.object_id_at_cursor: int = -1

    def get_initialization_commands(self) -> List[dict]:
        commands = super().get_initialization_commands()
        commands.extend([{"$type": "send_mouse",
                          "frequency": "always"},
                         {"$type": "send_mouse_raycast",
                          "raycast_id": FirstPersonCamera.MOUSE_RAYCAST_ID,
                          "avatar_id": self.avatar_id}])
        return commands

    def on_send(self, resp: List[bytes]) -> None:
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            # Get mouse data.
            if r_id == "mous":
                mouse = Mouse(resp[i])
                # TODO
            elif r_id == "rayc":
                raycast = Raycast(resp[i])
                # Got the raycast.
                if raycast.get_raycast_id() == FirstPersonCamera.MOUSE_RAYCAST_ID:
                    if raycast.get_hit():
                        self.commands.append({"$type": "look_at_position",
                                              "avatar_id": self.avatar_id,
                                              "position": TDWUtils.array_to_vector3(raycast.get_point())})
                        self.is_object_at_cursor = raycast.get_hit_object()
                        if raycast.get_hit_object():
                            self.object_id_at_cursor = raycast.get_object_id()
                    else:
                        self.is_object_at_cursor = False


        self.commands.append({"$type": "send_mouse_raycast",
                              "raycast_id": FirstPersonCamera.MOUSE_RAYCAST_ID,
                              "avatar_id": self.avatar_id})