import random
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import HumanoidLibrarian


"""
Add a [SMPL humanoid](https://smpl.is.tue.mpg.de/en) to the scene. Set its body parameters and play an animation.
"""

humanoid_librarian = HumanoidLibrarian("smpl_humanoids.json")
humanoid_record = random.choice(humanoid_librarian.records)

c = Controller()
c.start()
# These animations have been extracted from SMPL and are in their own library merely for organizational reasons.
# Other non-SMPL animations will work just as well with the SMPL humanoids and vice-versa.
animation_command, animation_record = c.get_add_humanoid_animation(humanoid_animation_name="walk_forward",
                                                                   library="smpl_animations.json")
humanoid_id = 0
commands = [TDWUtils.create_empty_room(12, 12),
            {"$type": "add_smpl_humanoid",
             "id": humanoid_id,
             "name": humanoid_record.name,
             "url": humanoid_record.get_url(),
             "position": {"x": 0, "y": 0, "z": 0},
             "rotation": {"x": 0, "y": 0, "z": 0},
             "height": random.uniform(-1, 1),
             "weight": random.uniform(-1, 1),
             "torso_height_and_shoulder_width": random.uniform(-1, 1),
             "chest_breadth_and_neck_height": random.uniform(-1, 1),
             "upper_lower_back_ratio": random.uniform(-1, 1),
             "pelvis_width": random.uniform(-1, 1),
             "hips_curve": random.uniform(-1, 1),
             "torso_height": random.uniform(-1, 1),
             "left_right_symmetry": random.uniform(-1, 1),
             "shoulder_and_torso_width": random.uniform(-1, 1)},
            animation_command,
            {"$type": "set_target_framerate",
             "framerate": 30}]
commands.extend(TDWUtils.create_avatar(position={"x": -3, "y": 1.7, "z": 0.5}))
look_at = {"$type": "look_at",
           "object_id": humanoid_id}
commands.append(look_at)
c.communicate(commands)
num_frames = animation_record.get_num_frames()
for i in range(4):
    c.communicate([{"$type": "play_humanoid_animation",
                    "name": animation_record.name,
                    "id": humanoid_id},
                   look_at])
    frame = 0
    while frame < num_frames:
        c.communicate(look_at)
        frame += 1
c.communicate({"$type": "terminate"})
