from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.drone import Drone
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Minimal example showing how to stop the drone's motor running.
"""

c = Controller()
drone = Drone(position={"x": 0, "y": 0, "z": 0}, rotation={"x": 0, "y": -90, "z": 0}, motor_on=True)
camera = ThirdPersonCamera(position={"x": 3.15, "y": 1.2, "z": 2},
                           look_at=drone.drone_id,
                           avatar_id="a")
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("drone_suburb")
capture = ImageCapture(avatar_ids=["a"], path=path)
print(f"Images will be saved to: {path}")
c.add_ons.extend([drone, camera, capture])
c.communicate(TDWUtils.create_empty_room(12, 12))
for i in range(200):
    c.communicate([])
# Start rising.
drone.set_lift(1)
for i in range(100):
    c.communicate([])
# Stop the motor.
drone.set_motor(False)
# The drone falls.
for i in range(200):
    c.communicate([])
c.communicate({"$type": "terminate"})
