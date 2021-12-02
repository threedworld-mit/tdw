from tdw.controller import Controller
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Add an HDRI skybox to the scene and rotate it.
"""

c = Controller()
camera = ThirdPersonCamera(avatar_id="a",
                           position={"x": -4.28, "y": 0.85, "z": 4.27},
                           look_at={"x": 0, "y": 0, "z": 0})
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("rotate_hdri_skybox")
print(f"Image will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"], path=path)
c.add_ons.extend([camera, capture])

# Load the scene. Add an HDRI skybox. Add an object.
# Set post-processing.
# Set the shadow strength to maximum.
object_id = c.get_unique_id()
c.communicate([c.get_add_scene(scene_name="building_site"),
               c.get_add_hdri_skybox("bergen_4k"),
               c.get_add_object(model_name="alma_floor_lamp",
                                object_id=object_id,
                                rotation={"x": 0, "y": 90, "z": 0}),
               {"$type": "set_post_exposure",
                "post_exposure": 0.6},
               {"$type": "set_contrast",
                "contrast": -20},
               {"$type": "set_saturation",
                "saturation": 10},
               {"$type": "set_screen_space_reflections",
                "enabled": False},
               {"$type": "set_shadow_strength",
                "strength": 1.0}])
# Rotate the skybox.
for i in range(48):
    c.communicate([{"$type": "look_at",
                    "object_id": object_id,
                    "use_centroid": True},
                   {"$type": "rotate_hdri_skybox_by",
                    "angle": 15}])
c.communicate({"$type": "terminate"})
