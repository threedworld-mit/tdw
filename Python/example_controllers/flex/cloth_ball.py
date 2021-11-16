from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Add a pressurized cloth ball to the scene.
"""

c = Controller()
camera = ThirdPersonCamera(avatar_id="a",
                           position={"x": 3.83, "y": 3.6, "z": -0.71},
                           look_at={"x": 0, "y": 0, "z": 0})
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("cloth_ball")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"], path=path)
c.add_ons.extend([camera, capture])
ball_id = c.get_unique_id()
c.communicate([TDWUtils.create_empty_room(12, 12),
               {'$type': 'convexify_proc_gen_room'},
               {'$type': 'create_flex_container'},
               c.get_add_object(model_name="sphere",
                                object_id=ball_id,
                                library="models_flex.json",
                                position={"x": 0, "y": 2, "z": 0}),
               {"$type": "set_flex_cloth_actor",
                "id": ball_id,
                "mass_scale": 1,
                "mesh_tesselation": 1,
                "tether_stiffness": 0.5,
                "bend_stiffness": 1.0,
                "self_collide": False,
                "stretch_stiffness": 1.0,
                "pressure": 0.9},
               {"$type": "assign_flex_container",
                "id": ball_id,
                "container_id": 0}])
for i in range(200):
    c.communicate([])
c.communicate({"$type": "terminate"})
