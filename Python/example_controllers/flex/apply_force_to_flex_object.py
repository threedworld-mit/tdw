from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Apply a directional force to a Flex soft-body object.
"""

c = Controller()
camera = ThirdPersonCamera(avatar_id="a",
                           position={"x": 3.83, "y": 3.6, "z": -0.71},
                           look_at={"x": 0, "y": 0, "z": 0})
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("apply_force_to_flex_object")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"], path=path)
c.add_ons.extend([camera, capture])
cube_id = c.get_unique_id()
c.communicate([TDWUtils.create_empty_room(12, 12),
               {'$type': 'convexify_proc_gen_room'},
               {'$type': 'create_flex_container'},
               c.get_add_object(model_name="cube",
                                object_id=cube_id,
                                library="models_flex.json",
                                position={"x": 0, "y": 0, "z": 0}),
               {'$type': 'set_flex_soft_actor',
                'id': cube_id,
                'particle_spacing': 0.125,
                'cluster_stiffness': 0.22},
               {"$type": "assign_flex_container",
                "id": cube_id,
                "container_id": 0},
               {"$type": "apply_force_to_flex_object",
                "force": {"x": 2000, "y": 0.0, "z": 0},
                "id": cube_id}])
for i in range(200):
    c.communicate([])
c.communicate({"$type": "terminate"})