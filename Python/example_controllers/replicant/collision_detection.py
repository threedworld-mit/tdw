from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.replicant.action_status import ActionStatus
from tdw.agents.arm import Arm


c = Controller()
r = Replicant()
# Disable obstacle avoidance so we can test collision detection.
r.collision_detection.avoid = False
c.add_ons.append(r)
trunk_id = Controller.get_unique_id()
# Create the room.
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(Controller.get_add_physics_object(model_name="trunck",
                                                  object_id=trunk_id,
                                                  position={"x": 0, "y": 0, "z": 3}))
c.communicate(commands)
r.move_by(7)
while r.action.status == ActionStatus.ongoing:
    c.communicate([])
print(r.action.status)
#c.communicate({"$type": "terminate"})
