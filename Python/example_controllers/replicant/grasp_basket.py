from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.replicant.action_status import ActionStatus
from tdw.agents.arm import Arm


c = Controller()
r = Replicant()
c.add_ons.append(r)
object_id = Controller.get_unique_id()
# Create the room.
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(Controller.get_add_physics_object(model_name="basket_18inx18inx12iin_wicker",
                                                  object_id=object_id,
                                                  position={"x": -2, "y": 0, "z": 3}))
c.communicate(commands)
r.move_to(target=object_id)
while r.action.status == ActionStatus.ongoing:
    c.communicate([])
r.reach_for(target=object_id, arms=Arm.right)
while r.action.status == ActionStatus.ongoing:
    c.communicate([])
r.grasp(target=object_id, arm=Arm.right)
while r.action.status == ActionStatus.ongoing:
    c.communicate([])
r.reach_for(target={"x": -2, "y": 1, "z": 3}, arms=Arm.right)
while r.action.status == ActionStatus.ongoing:
    c.communicate([])
