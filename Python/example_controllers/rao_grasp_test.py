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
AffordancePoints.AFFORDANCE_POINTS = {"basket_18inx18inx12iin_wicker": [{'x': -0.2285, 'y': 0.305, 'z': 0.0},
                                                           {'x': 0.2285, 'y': 0.305, 'z': 0.0},
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
basket_id = c.get_unique_id()
table_id = c.get_unique_id()
ball_id = c.get_unique_id()
ball_id2 = c.get_unique_id()
affordance_id = 0
reach_arm = "left"

replicant = Replicant(replicant_id=replicant_id, position={"x": -4, "y": 0, "z": 8}, image_frequency=ImageFrequency.never)
c.add_ons.append(replicant)
commands=[]
commands.extend([{"$type": "set_screen_size",
                           "width": 1920,
                           "height": 1080},
                          {"$type": "set_render_quality",
                           "render_quality": 5}])
commands.extend(c.get_add_physics_object(model_name="prim_sphere",
                               object_id=ball_id,
                               position={"x": 3.5, "y": 0, "z": -3.5},
                               rotation={"x": 0, "y": 0, "z": 0},
                               scale_factor={"x": 0.2, "y": 0.2, "z": 0.2},
                               kinematic=True,
                               gravity=False,
                               library="models_special.json"))
commands.extend(c.get_add_physics_object(model_name="prim_sphere",
                               object_id=ball_id2,
                               position={"x": -1, "y": 0, "z": -7.5},
                               rotation={"x": 0, "y": 0, "z": 0},
                               scale_factor={"x": 0.2, "y": 0.2, "z": 0.2},
                               kinematic=True,
                               gravity=False,
                               library="models_special.json"))
commands.extend(c.get_add_physics_object(model_name="live_edge_coffee_table",
                                         object_id=table_id,
                                         position={"x": -1, "y": 0, "z": 2},
                                         rotation={"x": 0, "y": 20, "z": 0},
                                         library="models_core.json"))
commands.extend(c.get_add_physics_object(model_name="zenblocks",
                                         object_id=c.get_unique_id(),
                                         position={"x": -1, "y": 0.65, "z": 2},
                                         scale_factor={"x": 0.5, "y": 0.5, "z": 0.5},
                                         mass=0.1,
                                         rotation={"x": 0, "y": 0, "z": 0}))

commands.extend(AffordancePoints.get_add_object_with_affordance_points(model_name="basket_18inx18inx12iin_wicker",
                                                                       object_id=basket_id,
                                                                       mass=2,
                                                                       position={"x": -1, "y": 0.35, "z": 2},
                                                                       rotation={"x": 0, "y": 0, "z": 0}))

c.communicate(commands)

replicant.move_to(target=table_id, arrived_offset=0.5)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])

replicant.reach_for(target=basket_id, arm="left", hand_position=np.array([0, 0, 0]))
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])

replicant.grasp(target=basket_id, arm="left")
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])

replicant.move_to(target=ball_id, arrived_offset=0.25)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])

replicant.drop(target=basket_id, arm="left")
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])

replicant.reset_arm(arm="left")
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])

replicant.move_to(target=ball_id2, arrived_offset=0.25)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])

logger.save()

#c.communicate({"$type": "terminate"})

