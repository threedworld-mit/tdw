from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.add_ons.logger import Logger
from tdw.replicant.action_status import ActionStatus
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Bounds
from tdw.replicant.arm import Arm
from tdw.replicant.affordance_points import AffordancePoints
from tdw.replicant.image_frequency import ImageFrequency
import numpy as np

"""
Create a humanoid that walks across the room, knocks over a chair and reaches for 
a randomly-positioned object multiple times.
"""

c = Controller(launch_build=False)
c.communicate(TDWUtils.create_empty_room(12, 20))
c.communicate(TDWUtils.create_avatar(position={"x": -0.5, "y": 1.175, "z": 6}, look_at={"x": 0.5, "y": 1, "z": 0}))

replicant_id=c.get_unique_id()
sofa_id=c.get_unique_id()
ball_id=c.get_unique_id()
reach_arm = Arm.both

replicant = Replicant(replicant_id=replicant_id, position={"x": 0, "y": 0, "z": 4}, image_frequency=ImageFrequency.never, avoid_objects=False)
c.add_ons.append(replicant)
commands=[]
commands.extend([{"$type": "set_screen_size",
                           "width": 1920,
                           "height": 1080},
                          {"$type": "set_render_quality",
                           "render_quality": 5},
                          c.get_add_object(model_name="arflex_strips_sofa",
                                           position={"x": 0, "y": 0, "z": 0},
                                           object_id=sofa_id),
                          {"$type": "send_bounds",
                           "frequency": "once"}])
commands.extend(c.get_add_physics_object(model_name="prim_sphere",
                               object_id=ball_id,
                               position={"x": 0, "y": 0, "z": -4.0},
                               rotation={"x": 0, "y": 0, "z": 0},
                               scale_factor={"x": 0.2, "y": 0.2, "z": 0.2},
                               kinematic=True,
                               gravity=False,
                               library="models_special.json"))
resp = c.communicate(commands)

replicant.collision_detection.objects = True
replicant.collision_detection.walls = True

for i in range(100):
    replicant.move_to(target=ball_id, arrived_offset=0.25)
    while replicant.action.status == ActionStatus.ongoing:
        c.communicate([])
    print(replicant.action.status)



#c.communicate({"$type": "terminate"})

