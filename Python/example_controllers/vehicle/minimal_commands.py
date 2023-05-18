from tdw.controller import Controller
from tdw.add_ons.third_person_camera import ThirdPersonCamera

"""
Minimal example of a vehicle driving in a suburb.
"""

c = Controller(launch_build=False)
vehicle_id = 999
camera = ThirdPersonCamera(position={"x": 7, "y": 2.5, "z": -1},
                           look_at=vehicle_id,
                           avatar_id="a")
c.add_ons.append(camera)
c.communicate([c.get_add_scene(scene_name="suburb_scene_2023"),
               {"$type": "add_vehicle", 
                     "id": vehicle_id,
                     "name": "all_terrain_vehicle",
                     "rotation": {"x": 0, "y": -90, "z": 0},
                     "url": "https://tdw-public.s3.amazonaws.com/vehicles/windows/2020.3/all_terrain_vehicle"}])
for i in range(50):
    c.communicate([])
# Drive up the street slowly.
c.communicate({"$type": "apply_vehicle_drive", "id": vehicle_id, "force": 0.25})
for i in range(20):
    c.communicate([])
#Speed up a bit.
c.communicate({"$type": "apply_vehicle_drive", "id": vehicle_id, "force": 0.5})
for i in range(235):
    c.communicate([])
# Turn then continue straight.
c.communicate([{"$type": "apply_vehicle_drive", "id": vehicle_id, "force": 0.25},
               {"$type": "apply_vehicle_turn", "id": vehicle_id, "force": 1.0}])
for i in range(300):
    c.communicate([])
c.communicate({"$type": "apply_vehicle_turn", "id": vehicle_id, "force": 0})
c.communicate({"$type": "apply_vehicle_drive", "id": vehicle_id, "force": 1.0})
for i in range(300):
    c.communicate([])
# Stop for 200 frames.
c.communicate({"$type": "apply_vehicle_drive", "id": vehicle_id, "force": 0})
for i in range(200):
    c.communicate([])
#c.communicate({"$type": "terminate"})
