from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.drone import Drone
from tdw.drone.drone_dynamic import DroneDynamic
from tdw.add_ons.third_person_camera import ThirdPersonCamera

"""
Minimal drone dynamic data example.
"""

c = Controller(launch_build=False)
# We want to stop rising when the drone reaches this height.
altitude_ceiling = 10
cruise_level = 2
drone = Drone(position={"x": 0, "y": 0, "z": 0}, rotation={"x": 0, "y": -90, "z": 0})
camera = ThirdPersonCamera(position={"x": 3.15, "y": 1.2, "z": 2},
                           look_at=drone.drone_id,
                           avatar_id="a")
c.add_ons.extend([drone, camera])
c.communicate([c.get_add_scene(scene_name="suburb_scene_2023"),
              {"$type": "set_screen_size",
               "width": 1920,
               "height": 1080}])
for i in range(200):
    c.communicate([])
# Start rising.
drone.set_lift(1)
while TDWUtils.array_to_vector3(drone.dynamic.transform.position)["y"] < altitude_ceiling:
    c.communicate([])
# Stop rising and hover for a bit.
drone.set_lift(0)
print("Reached altitude ceiling")
for i in range(100):
    c.communicate([])
# Fly down the street, dropping to "cruise_level" then continue.
drone.set_drive(1)
drone.set_lift(-1)
while TDWUtils.array_to_vector3(drone.dynamic.transform.position)["y"] > cruise_level:
    c.communicate([])
drone.set_lift(0)
print("Reached cruise level")
for i in range(400):
    c.communicate([])
c.communicate({"$type": "terminate"})



