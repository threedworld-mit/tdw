from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.add_ons.logger import Logger
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.arm import Arm
from tdw.replicant.affordance_points import AffordancePoints
from tdw.replicant.image_frequency import ImageFrequency
import numpy as np

"""
Create a humanoid that walks across the room, knocks over a chair and reaches for 
a randomly-positioned object multiple times.
"""

# A dictionary of affordance points per model. This could be saved to a json file.
AffordancePoints.AFFORDANCE_POINTS = {"basket_18inx18inx12iin_wicker": [
                                                           #{'x': -0.2285, 'y': 0.305, 'z': 0.0},
                                                           #{'x': 0.2285, 'y': 0.305, 'z': 0.0},
                                                           {'x': 0, 'y': 0.305, 'z': 0.2285},
                                                           {'x': 0, 'y': 0.305, 'z': -0.2285}],
                                      "basket_18inx18inx12iin_bamboo": [{'x': -0.2285, 'y': 0.305, 'z': 0.0},
                                                           {'x': 0.2285, 'y': 0.305, 'z': 0.0},
                                                           {'x': 0, 'y': 0.305, 'z': 0.2285},
                                                           {'x': 0, 'y': 0.305, 'z': -0.2285}]}

c = Controller(launch_build=False)

logger = Logger(record=True, path="log.json")
c.add_ons.append(logger)
c.communicate([])
c.communicate(TDWUtils.create_empty_room(12, 20))
c.communicate(TDWUtils.create_avatar(position={"x": -0.5, "y": 1.175, "z": 6}, look_at={"x": 0.5, "y": 1, "z": 0}))

replicant_id=c.get_unique_id()
chair_id=c.get_unique_id()
basket_id = c.get_unique_id()
table_id = c.get_unique_id()
ball_id = c.get_unique_id()
ball_id2 = c.get_unique_id()
affordance_id = 0
reach_arm = Arm.both

print("Chair ID = " + str(chair_id))
print("basket ID = " + str(basket_id))
print("table ID = " + str(table_id))
print("ball ID = " + str(ball_id))


replicant = Replicant(replicant_id=replicant_id, position={"x": 0, "y": 0, "z": -8}, image_frequency=ImageFrequency.never, avoid_objects=False)
c.add_ons.append(replicant)
commands=[]
commands.extend([{"$type": "set_screen_size",
                           "width": 1920,
                           "height": 1080},
                          {"$type": "set_render_quality",
                           "render_quality": 5},
                 c.get_add_object(model_name="chair_billiani_doll",
                                     object_id=chair_id,
                                     position={"x": 0, "y": 0, "z": 0},
                                     rotation={"x": 0, "y": 63.25, "z": 0}),
                 c.get_add_object(model_name="live_edge_coffee_table",
                                         object_id=table_id,
                                         position={"x": 0, "y": 0, "z": 2},
                                         rotation={"x": 0, "y": 20, "z": 0},
                                         library="models_core.json")])
commands.extend(c.get_add_physics_object(model_name="prim_sphere",
                               object_id=ball_id,
                               position={"x": 0, "y": 0, "z": 4.0},
                               rotation={"x": 0, "y": 0, "z": 0},
                               scale_factor={"x": 0.2, "y": 0.2, "z": 0.2},
                               kinematic=True,
                               gravity=False,
                               library="models_special.json"))
commands.extend(c.get_add_physics_object(model_name="prim_sphere",
                               object_id=ball_id2,
                               position={"x": 5, "y": 0, "z": 3.5},
                               rotation={"x": 0, "y": 0, "z": 0},
                               scale_factor={"x": 0.2, "y": 0.2, "z": 0.2},
                               kinematic=True,
                               gravity=False,
                               library="models_special.json"))


c.communicate(commands)

replicant.collision_detection.objects = False
#replicant.collision_detection.exclude_objects = [chair_id]

replicant.turn_by(angle=60.0)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])

replicant.move_by(distance=3.3)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])
"""
replicant.move_to(target=ball_id2, arrived_offset=0.2)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])
"""
print(replicant.action.status, replicant.dynamic.position)

#logger.save()

#c.communicate({"$type": "terminate"})

