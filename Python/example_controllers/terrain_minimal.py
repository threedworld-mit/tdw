from tdw.controller import Controller
from tdw.add_ons.vehicle import Vehicle
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Minimal example of a vehicle driving in a suburb.
"""

c = Controller(launch_build=False)
vehicle = Vehicle(position={"x": 0, "y": 29.6, "z": 58.6},
                  rotation={"x": 0, "y": 0, "z": 0},
                  image_capture=False)
camera = ThirdPersonCamera(position={"x": 0, "y": 32.0, "z": 60.0},
                           look_at=vehicle.vehicle_id,
                           follow_object=vehicle.vehicle_id,
                           avatar_id="a")
c.add_ons.extend([vehicle, camera])
c.communicate([c.get_add_scene(scene_name="terrain_3x3_scene")])
for i in range(50):
    c.communicate([])
# Drive up the street.
vehicle.set_drive(1)
for i in range(360):
    c.communicate([])
# Slow down.
vehicle.set_drive(0.2)
vehicle.set_brake(0.2)
for i in range(240):
    c.communicate([])
# Turn into the driveway.
vehicle.set_brake(0)
vehicle.set_turn(1)
vehicle.set_drive(0)
for i in range(150):
    c.communicate([])
# Hit the brakes.
vehicle.set_turn(0)
vehicle.set_brake(0.5)
for i in range(50):
    c.communicate([])
#c.communicate({"$type": "terminate"})
