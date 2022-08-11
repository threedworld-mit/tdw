from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.embodied_avatar import EmbodiedAvatar
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.add_ons.avatar_body import AvatarBody
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Embodied avatar example.
"""

c = Controller()
embodied_avatar = EmbodiedAvatar(avatar_id="a",
                                 body=AvatarBody.capsule,
                                 position={"x": 1.5, "y": 0, "z": 0.3},
                                 rotation={"x": 0, "y": 30, "z": 0},
                                 color={"r": 0.6, "g": 0.3, "b": 0, "a": 1})
camera = ThirdPersonCamera(avatar_id="c",
                           position={"x": 0, "y": 9.4, "z": -4.4},
                           look_at={"x": 0, "y": 0.6, "z": 0})
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("embodied_avatar")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a", "c"], path=path)
c.add_ons.extend([embodied_avatar, camera, capture])
c.communicate(TDWUtils.create_empty_room(12, 12))
embodied_avatar.apply_force(500)
embodied_avatar.apply_torque(-400)
while embodied_avatar.is_moving:
    c.communicate([])
c.communicate({"$type": "terminate"})
