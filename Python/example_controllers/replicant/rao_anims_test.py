from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.add_ons.logger import Logger
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.image_frequency import ImageFrequency
from tdw.replicant.actions.perform_action_sequence import PerformActionSequence
import numpy as np

"""
Create a humanoid that walks across the room, then performs a sequence of
motion-capture animations.
"""

c = Controller(launch_build=False)

c.communicate([])
c.communicate(TDWUtils.create_empty_room(12, 20))
c.communicate(TDWUtils.create_avatar(position={"x": -0.5, "y": 1.175, "z": 6}, look_at={"x": 0.5, "y": 1, "z": 0}))

replicant_id=c.get_unique_id()

replicant = Replicant(replicant_id=replicant_id, position={"x": 0, "y": 0, "z": 0}, image_frequency=ImageFrequency.never)
c.add_ons.append(replicant)
commands=[]
commands.extend([{"$type": "set_screen_size",
                           "width": 1920,
                           "height": 1080},
                          {"$type": "set_render_quality",
                           "render_quality": 5}])
c.communicate(commands)

anim_list = ["mop_floor", "clean_windows", "smoke_cigarette_1", "open_can_drink", "hammering"]

replicant.move_to(target={"x": 1, "y": 0, "z": -6.5}, arrived_offset=0.25)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])

replicant.perform_action_sequence(animation_list=anim_list)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])

#c.communicate({"$type": "terminate"})

