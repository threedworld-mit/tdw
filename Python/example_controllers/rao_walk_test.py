from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.add_ons.logger import Logger
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.arm import Arm
import numpy as np

"""
Create a humanoid that walks across the room, knocks over a chair and reaches for 
a randomly-positioned object multiple times.
"""

c = Controller(launch_build=False)

logger = Logger(record=True, path="log.json")
c.add_ons.append(logger)
c.communicate([])
c.communicate(TDWUtils.create_empty_room(12, 12))
c.communicate(TDWUtils.create_avatar(position={"x": 2, "y": 1.5, "z": 4}, look_at={"x": 2.05, "y": 1, "z": 2.05}))

ball_id1 = c.get_unique_id()
ball_id2 = c.get_unique_id()
ball_id3 = c.get_unique_id()
replicant = Replicant(replicant_id=c.get_unique_id(), position={"x": 0, "y": 0, "z": -4})
c.add_ons.append(replicant)
commands=[]
commands.extend(c.get_add_physics_object(model_name="prim_sphere",
                               object_id=ball_id1,
                               position={"x": 3, "y": 0, "z": -1.5},
                               rotation={"x": 0, "y": 0, "z": 0},
                               scale_factor={"x": 0.2, "y": 0.2, "z": 0.2},
                               kinematic=True,
                               gravity=False,
                               library="models_special.json"))
commands.extend(c.get_add_physics_object(model_name="prim_sphere",
                               object_id=ball_id2,
                               position={"x": -2, "y": 0, "z": 1.5},
                               rotation={"x": 0, "y": 0, "z": 0},
                               scale_factor={"x": 0.2, "y": 0.2, "z": 0.2},
                               kinematic=True,
                               gravity=False,
                               library="models_special.json"))
commands.extend(c.get_add_physics_object(model_name="prim_sphere",
                               object_id=ball_id3,
                               position={"x": 2, "y": 0, "z": 2},
                               rotation={"x": 0, "y": 0, "z": 0},
                               scale_factor={"x": 0.2, "y": 0.2, "z": 0.2},
                               kinematic=True,
                               gravity=False,
                               library="models_special.json"))
c.communicate(commands)
#replicant.turn_to(target=chair_id)
#while replicant.action.status == ActionStatus.ongoing:
    #c.communicate([])
#replicant.move_to(target={"x": 3, "y": 0, "z": -1.5})


replicant.move_to(target=ball_id1)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])

replicant.move_to(target=ball_id2)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])

replicant.move_to(target=ball_id3)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])

replicant.reach_for(target={"x": 2, "y": 1.75, "z": 1.75}, arm=Arm.left, hand_position=np.array([0, 0, 0]))
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])

logger.save()

#c.communicate({"$type": "terminate"})

