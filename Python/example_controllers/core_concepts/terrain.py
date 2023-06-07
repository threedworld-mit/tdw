from tdw.controller import Controller
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Load a large outdoor scene.
"""

c = Controller()
camera = ThirdPersonCamera(position={"x": -12.1, "y": 60, "z": 492},
                           look_at={"x": 0, "y": 58, "z": 0},
                           avatar_id="a")
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("terrain")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"], path=path)
c.add_ons.extend([camera, capture])
c.communicate([c.get_add_scene(scene_name="terrain_3x3_scene"),
               {"$type": "set_screen_size",
                "width": 1280,
                "height": 720}])
c.communicate([{"$type": "set_camera_clipping_planes",
                "near": 1.0,
                "far": 10000,
                "avatar_id": "a"},
               {"$type": "set_focus_distance",
                "focus_distance": 2.5}])
c.communicate({"$type": "terminate"})
