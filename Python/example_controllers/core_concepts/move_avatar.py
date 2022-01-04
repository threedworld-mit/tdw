from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

"""
Move the avatar and rotate the camera.
Note that in this example, the `avatar_id` parameters are missing. That's because they all default to "a".
"""

c = Controller()
y = 5.7
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "create_avatar",
                "type": "A_Img_Caps_Kinematic",
                "id": "a"},
               {"$type": "teleport_avatar_to",
                "position": {"x": -1, "y": y, "z": -3.8}},
               {"$type": "rotate_sensor_container_by",
                "axis": "pitch",
                "angle": 26},
               {"$type": "set_target_framerate",
                "framerate": 30}])
for i in range(20):
    y += 0.1
    c.communicate([{"$type": "rotate_sensor_container_by",
                    "axis": "yaw",
                    "angle": 2},
                   {"$type": "teleport_avatar_to",
                    "position": {"x": -1, "y": y, "z": -3.8}}])
c.communicate({"$type": "terminate"})
