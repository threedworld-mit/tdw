from tdw.controller import Controller
from tdw.add_ons.drone import Drone
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Minimal example of a drone flying in a suburb.
"""

c = Controller()
drone = Drone()
camera = ThirdPersonCamera(position={"x": 3.15, "y": 1.2, "z": 2},
                           look_at=drone.drone_id,
                           avatar_id="a")
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("drone_suburb")
capture = ImageCapture(avatar_ids=["a"], path=path)
print(f"Images will be saved to: {path}")
c.add_ons.extend([drone, camera, capture])
c.communicate([c.get_add_scene(scene_name="suburb_scene_2023")])
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
for i in range(200):
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
