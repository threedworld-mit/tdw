from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.drone import Drone
from tdw.add_ons.third_person_camera import ThirdPersonCamera

"""
Minimal drone  example.
"""

c = Controller(launch_build=False)
drone = Drone(position={"x": 0, "y": 0, "z": 0})
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
for i in range(100):
    c.communicate([])
# Hold this altitude.
drone.set_lift(0)
# Fly forward.
drone.set_drive(1)
for i in range(100):
    c.communicate([])
# Turn a little then continue straight.
drone.set_turn(-1)
for i in range(100):
    c.communicate([])
drone.set_turn(0)
for i in range(100):
    c.communicate([])
# Stop and hover for 200 frames.
drone.set_drive(0)
for i in range(200):
    c.communicate([])
# Return to the ground.
drone.set_lift(-1)
for i in range(100):
    c.communicate([])
# Watch for a bit.
drone.set_lift(0)
for i in range(200):
    c.communicate([])
c.communicate({"$type": "terminate"})


