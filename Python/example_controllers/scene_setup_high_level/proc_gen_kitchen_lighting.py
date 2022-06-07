import numpy as np
from tdw.controller import Controller
from tdw.add_ons.proc_gen_kitchen import ProcGenKitchen
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.add_ons.interior_scene_lighting import InteriorSceneLighting
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
ProcGenKitchen with realistic lighting.
"""

path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("proc_gen_kitchen_lighting")
print(f"Images will be saved to: {path}")
proc_gen_kitchen = ProcGenKitchen()
random_seed = 14
proc_gen_kitchen.create(rng=np.random.RandomState(random_seed))
interior_scene_lighting = InteriorSceneLighting(rng=np.random.RandomState(random_seed))
camera = ThirdPersonCamera(position={"x": -1, "y": 1.8, "z": 2},
                           look_at={"x": 0, "y": 1, "z": 0},
                           avatar_id="a")
capture = ImageCapture(avatar_ids=["a"], path=path, pass_masks=["_img"])
c = Controller()
c.add_ons.extend([proc_gen_kitchen, interior_scene_lighting, camera, capture])
c.communicate([{"$type": "set_screen_size",
                "width": 1280,
                "height": 720}])
c.communicate({"$type": "terminate"})
