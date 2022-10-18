from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.add_ons.image_capture import ImageCapture
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.image_frequency import ImageFrequency
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Look at an object and a position, then reset the head.
"""

def do_action(status: ActionStatus = ActionStatus.success):
    while replicant.action.status == ActionStatus.ongoing:
        c.communicate([])
    assert replicant.action.status == status, replicant.action.status


c = Controller()
replicant = Replicant(image_frequency=ImageFrequency.always)
c.add_ons.append(replicant)
object_id = Controller.get_unique_id()
# Create the room. Set a target target.
commands = [TDWUtils.create_empty_room(12, 12),
            {"$type": "set_target_framerate",
             "framerate": 60}]
commands.extend(Controller.get_add_physics_object(model_name="basket_18inx18inx12iin_wicker",
                                                  object_id=object_id,
                                                  position={"x": -2, "y": 0, "z": 3}))
commands.extend(Controller.get_add_physics_object(model_name="rh10",
                                                  object_id=Controller.get_unique_id(),
                                                  position={"x": 2, "y": 0, "z": 3}))
c.communicate(commands)
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("replicant_look_at")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=[replicant.static.avatar_id], path=path)
c.add_ons.append(capture)
c.communicate([])
replicant.look_at(target=object_id)
do_action()
replicant.look_at(target={"x": 2, "y": 0.3, "z": 3})
do_action()
replicant.reset_head()
do_action()
c.communicate({"$type": "terminate"})
