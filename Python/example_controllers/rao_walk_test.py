from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.add_ons.logger import Logger
from tdw.replicant.action_status import ActionStatus

"""
Create a humanoid that walks across the room, knocks over a chair and reaches for 
a randomly-positioned object multiple times.
"""

c = Controller(launch_build=False)

logger = Logger(record=True, path="log.json")
c.add_ons.append(logger)
c.communicate([])
c.communicate(TDWUtils.create_empty_room(12, 12))
c.communicate(TDWUtils.create_avatar(position={"x": -3, "y": 1.5, "z": 4}, look_at={"x": 0, "y": 1.0, "z": 0}))

chair_id = c.get_unique_id()
replicant = Replicant(replicant_id=c.get_unique_id(), position={"x": 0, "y": 0, "z": -4})
c.add_ons.append(replicant)
c.communicate(c.get_add_object(model_name="chair_billiani_doll",
                               object_id=chair_id,
                               position={"x": 3, "y": 0, "z": -1.5},
                               rotation={"x": 0, "y": 63.25, "z": 0},
                               library="models_core.json"))
#replicant.turn_to(target=chair_id)
#while replicant.action.status == ActionStatus.ongoing:
    #c.communicate([])
replicant.move_to(target={"x": 3, "y": 0, "z": -1.5})
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])
print(replicant.action.status, replicant.dynamic.position)
logger.save()
#c.communicate({"$type": "terminate"})

