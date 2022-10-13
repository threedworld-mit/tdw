from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.replicant.action_status import ActionStatus
from tdw.agents.arm import Arm


c = Controller()
r = Replicant()
c.add_ons.append(r)
trunk_id = Controller.get_unique_id()
mug_id = Controller.get_unique_id()
print(trunk_id, mug_id)
# Create the room.
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(Controller.get_add_physics_object(model_name="trunck",
                                                  object_id=trunk_id,
                                                  position={"x": 0, "y": 0, "z": 3},
                                                  kinematic=True))
commands.extend(Controller.get_add_physics_object(model_name="coffeemug",
                                                  object_id=mug_id,
                                                  position={"x": 0, "y": 0.9888946, "z": 3}))
c.communicate(commands)
r.move_to(target=trunk_id)
while r.action.status == ActionStatus.ongoing:
    c.communicate([])
r.reach_for(target=mug_id, arms=Arm.right)
while r.action.status == ActionStatus.ongoing:
    c.communicate([])
print(r.action.status)
r.grasp(target=mug_id, arm=Arm.right)
while r.action.status == ActionStatus.ongoing:
    c.communicate([])
print(r.action.status)
r.reset_arm(arms=[Arm.left, Arm.right])
while r.action.status == ActionStatus.ongoing:
    c.communicate([])
r.move_by(-4)
while r.action.status == ActionStatus.ongoing:
    c.communicate([])
print(r.action.status)
c.communicate({"$type": "terminate"})
