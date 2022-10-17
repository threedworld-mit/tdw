from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.replicant.action_status import ActionStatus
from tdw.agents.arm import Arm
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


c = Controller()
replicant = Replicant()
camera = ThirdPersonCamera(position={"x": 2, "y": 3, "z": 0.3},
                           look_at=replicant.replicant_id,
                           avatar_id="a")
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("replicant_reach_too_far")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=[camera.avatar_id], path=path)
c.add_ons.extend([replicant, camera, capture])
object_id = Controller.get_unique_id()
# Create the room. Set a target target.
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(Controller.get_add_physics_object(model_name="basket_18inx18inx12iin_wicker",
                                                  object_id=object_id,
                                                  position={"x": -2, "y": 0, "z": 3}))
c.communicate(commands)
# The object is too far away.
replicant.reach_for(target=object_id, arms=Arm.right)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])
assert replicant.action.status == ActionStatus.failed_to_reach, replicant.action.status
# Try to reach the object anyway and fail.
replicant.reach_for(target=object_id, arms=Arm.right, max_distance=4)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])
assert replicant.action.status == ActionStatus.failed_to_reach, replicant.action.status
c.communicate({"$type": "terminate"})
