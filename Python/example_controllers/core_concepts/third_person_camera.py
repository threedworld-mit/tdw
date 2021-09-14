from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera

"""
Create a simple scene and add a third-person camera avatar.
"""

c = Controller()

# Create the third-person camera.
cam = ThirdPersonCamera(avatar_id="a",
                        position={"x": -1, "y": 5.7, "z": -3.8},
                        rotation={"x": 26, "y": 0, "z": 0})

# Append the third-person camera add-on.
c.add_ons.append(cam)
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "set_target_framerate",
                "framerate": 30}])
for i in range(20):
    # Raise the camera up by 0.1 meters.
    cam.teleport(position={"x": 0, "y": 0.1, "z": 0},
                 absolute=False)
    # Rotate around the yaw axis by 2 degrees.
    cam.rotate(rotation={"x": 0, "y": 2, "z": 0})
    c.communicate([])
c.communicate({"$type": "terminate"})
