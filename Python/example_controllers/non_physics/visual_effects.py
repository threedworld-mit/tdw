from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.audio_initializer import AudioInitializer
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Add non-physical visual effects to the scene.
"""

c = Controller()
camera = ThirdPersonCamera(position={"x": 0.5, "y": 1.6, "z": -4.6},
                           look_at={"x": 0, "y": 0, "z": 0},
                           avatar_id="a")
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("visual_effects")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"], path=path)
audio = AudioInitializer()
c.add_ons.extend([camera, capture, audio])
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "set_screen_size",
                "width": 512,
                "height": 512},
               c.get_add_visual_effect(name="fire",
                                       position={"x": 0, "y": 0, "z": 0},
                                       effect_id=Controller.get_unique_id()),
               c.get_add_visual_effect(name="smoke",
                                       position={"x": 0, "y": 0, "z": 0},
                                       effect_id=Controller.get_unique_id())])
for i in range(200):
    c.communicate([])
c.communicate({"$type": "terminate"})
