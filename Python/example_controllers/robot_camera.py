from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

"""
Add a camera to a Magnebot.
"""


if __name__ == "__main__":
    c = Controller(launch_build=False)
    c.start()
    c.communicate([TDWUtils.create_empty_room(12, 12),
                   {"$type": "add_magnebot",
                    "position": {"x": 0, "y": 0, "z": 0},
                    "rotation": 0,
                    "id": 0},
                   {"$type": "create_avatar",
                    "type": "A_Img_Caps_Kinematic",
                    "id": "a"},
                   {"$type": "parent_avatar_to_robot",
                    "position": {"x": 0, "y": 0.053, "z": 0.1838},
                    "id": 0,
                    "avatar_id": "a",
                    "body_part": "torso"}])
