from tdw.controller import Controller
from tdw.add_ons.vehicle import Vehicle
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Minimal example of a vehicle driving in a suburb.
"""

c = Controller()
vehicle = Vehicle(rotation={"x": 0, "y": -90, "z": 0}, image_capture=False)
camera = ThirdPersonCamera(position={"x": 7, "y": 2.5, "z": -1},
                           look_at=vehicle.vehicle_id,
                           avatar_id="a")
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("vehicle_suburb")
capture = ImageCapture(avatar_ids=["a"], path=path)
print(f"Images will be saved to: {path}")
c.add_ons.extend([vehicle, camera, capture])
c.add_ons.extend([vehicle, camera])
c.communicate([c.get_add_scene(scene_name="suburb_scene_2023")])
for i in range(50):
    c.communicate([])
# Drive up the street slowly.
vehicle.set_drive(0.5)
for i in range(300):
    c.communicate([])
# Speed up a bit.
vehicle.set_drive(0.75)
for i in range(450):
    c.communicate([])
# Turn then continue straight.
vehicle.set_drive(0.25)
vehicle.set_turn(1.0)
for i in range(250):
    c.communicate([])
vehicle.set_drive(1.0)
vehicle.set_turn(0)
for i in range(300):
    c.communicate([])
# Stop for 200 frames.
vehicle.set_drive(0)
for i in range(200):
    c.communicate([])
c.communicate({"$type": "terminate"})
