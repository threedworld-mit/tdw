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
c.communicate(TDWUtils.create_avatar(position={"x": -4.42, "y": 1.5, "z": 5.95}, look_at={"x": 0, "y": 1.0, "z": 0}))


replicant = Replicant(replicant_id=c.get_unique_id())
c.add_ons.append(replicant)
c.communicate([])
replicant.move_by(distance=8)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])
logger.save()
c.communicate({"$type": "terminate"})

