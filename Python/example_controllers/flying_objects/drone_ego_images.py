from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.drone import Drone
from tdw.drone.drone_dynamic import DroneDynamic
from tdw.drone.image_frequency import ImageFrequency
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Minimal drone  example.
"""

path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("drone_egocentric")
print(f"Images will be saved to: {path}")
c = Controller(launch_build=False)
drone = Drone(position={"x": 0, "y": 0, "z": 0}, image_frequency=ImageFrequency.never)
camera = ThirdPersonCamera(position={"x": 3.15, "y": 1.2, "z": 2},
                           look_at=drone.drone_id,
                           avatar_id="a")
c.add_ons.extend([drone, camera])
c.communicate([c.get_add_scene(scene_name="suburb_scene_2023"),
              {"$type": "set_screen_size",
               "width": 1920,
               "height": 1080}])
# Start rising.
drone.set_lift(1)
for i in range(300):
    c.communicate([])
    # Save the images.
    drone.dynamic.save_images(output_directory=path)
# Fly forward, still rising.
drone.set_drive(1)
for i in range(200):
    c.communicate([])
    # Save the images.
    drone.dynamic.save_images(output_directory=path)
# Hold current altitude, turn a little then continue straight.
drone.set_lift(0)
drone.set_turn(-1)
for i in range(100):
    c.communicate([])
    drone.dynamic.save_images(output_directory=path)
drone.set_turn(0)
for i in range(300):
    c.communicate([])
    # Save the images.
    drone.dynamic.save_images(output_directory=path)
# Stop and hover for 50 frames.
drone.set_drive(0)
for i in range(50):
    c.communicate([])
    # Save the images.
    drone.dynamic.save_images(output_directory=path)
# Return to the ground.
drone.set_lift(-1)
for i in range(600):
    c.communicate([])
    # Save the images.
    drone.dynamic.save_images(output_directory=path)
drone.set_lift(0)
c.communicate({"$type": "terminate"})
