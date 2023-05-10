from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

"""
Minimal drone  example.
"""

c = Controller(launch_build=False)
drone_id = 1
avatar_id = 2
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "add_drone", 
                "id": drone_id,
                "name":"drone", 
                "url": "https://tdw-public.s3.amazonaws.com/flying_objects/windows/2020.3/drone", 
                "position": {"x": 2, "y": 0.2, "z": -4},
                "rise_speed": 3,
                "lower_speed":3,
                 "forward_speed": 2.5,
                 "enable_lights": False}])

c.communicate([{"$type": "create_avatar",
                "type": "A_Img_Caps_Kinematic",
                "id": avatar_id},
               {"$type": "set_pass_masks",
                "pass_masks": ["_img", "_id", "_depth"],
                "avatar_id": avatar_id},
                {"$type": "parent_avatar_to_drone",
                "position": {"x": -0.1, "y": -0.1, "z": 0},
                "avatar_id": avatar_id,
                "id": drone_id},
               {"$type": "enable_image_sensor",
                "enable": False,
                "avatar_id": avatar_id},
               {"$type": "set_img_pass_encoding",
                "value": False},
               {"$type": "rotate_sensor_container_by", "axis": "pitch", "angle": 45.0}])

# At rest on ground.
for i in range(200):
     c.communicate([])

# Lift into the air.
for i in range(100):
     c.communicate({"$type": "apply_lift_force_to_drone", "id": 1, "force": 1.0})

# Hover.
for i in range(150):
     c.communicate({"$type": "apply_lift_force_to_drone", "id": 1, "force": 0})

# Fly forward.
for i in range(300):
     c.communicate({"$type": "apply_drive_force_to_drone", "id": 1, "force": 1.0})

# Hover some more. Lift force is still 0, so no need to keep sending.
for i in range(400):
     c.communicate({"$type": "apply_drive_force_to_drone", "id": 1, "force": 0})

# Fly back and drop a little.
for i in range(50):
     c.communicate([{"$type": "apply_drive_force_to_drone", "id": 1, "force": -1},
                    {"$type": "apply_lift_force_to_drone", "id": 1, "force": -1}])

# Fly back and turn a little. Note lift force of zero, to maintain current height.
for i in range(100):
     c.communicate([{"$type": "apply_drive_force_to_drone", "id": 1, "force": -1},
                    {"$type": "apply_lift_force_to_drone", "id": 1, "force": 0},
                    {"$type": "apply_turn_force_to_drone", "id": 1, "force": 1}])

# Hover some more. Lift force is still 0, so no need to keep sending.
for i in range(200):
     c.communicate([{"$type": "apply_drive_force_to_drone", "id": 1, "force": 0},
                   {"$type": "apply_turn_force_to_drone", "id": 1, "force": 0}])

# Drop back to the ground. Drive and turn forces are still 0, so no need to keep sending.
for i in range(100):
     c.communicate({"$type": "apply_lift_force_to_drone", "id": 1, "force": -1})

