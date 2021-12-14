import random
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.output_data import OutputData, Raycast

"""
Use spherecast data to place an object in a bowl.
"""

c = Controller()
bowl_id = c.get_unique_id()

camera = ThirdPersonCamera(position={"x": 0.5, "y": 1.6, "z": -1},
                           look_at=bowl_id,
                           avatar_id="a")
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("spherecast")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=[camera.avatar_id], path=path, png=True)
c.add_ons.extend([camera, capture])

bowl_position = {"x": -1, "y": 0, "z": 0.5}

raycast_id = c.get_unique_id()
resp = c.communicate([TDWUtils.create_empty_room(12, 12),
                      c.get_add_object(position=bowl_position,
                                       object_id=bowl_id,
                                       model_name="round_bowl_small_walnut"),
                      {"$type": "send_spherecast",
                       "radius": 0.3,
                       "origin": {"x": bowl_position["x"], "y": 100, "z": bowl_position["z"]},
                       "destination": {"x": bowl_position["x"], "y": -100, "z": bowl_position["z"]},
                       "id": raycast_id}])
hits = []
for i in range(len(resp) - 1):
    r_id = OutputData.get_data_type_id(resp[i])
    if r_id == "rayc":
        raycast = Raycast(resp[i])
        if raycast.get_raycast_id() == raycast_id:
            if raycast.get_hit() and raycast.get_hit_object() and raycast.get_object_id() == bowl_id:
                hits.append(raycast.get_point())
jug_position = random.choice(hits)
# Add an object at a random position on the bowl.
c.communicate(c.get_add_object(model_name="jug03",
                               position=TDWUtils.array_to_vector3(jug_position),
                               object_id=c.get_unique_id()))
c.communicate({"$type": "terminate"})