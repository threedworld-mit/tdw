from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.add_ons.replicant import Replicant
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.arm import Arm
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


"""
Walk to an object, grasp it, walk away, and drop it.
"""

c = Controller()
replicant = Replicant()
camera = ThirdPersonCamera(position={"x": -1.5, "y": 1.175, "z": 5.25},
                           look_at={"x": 0.5, "y": 1, "z": 0},
                           avatar_id="a")
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("replicant_go_to_grasp")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"], path=path)
c.add_ons.extend([replicant, camera, capture])
trunk_id = Controller.get_unique_id()
mug_id = Controller.get_unique_id()
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
replicant.move_to(target=trunk_id)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])
replicant.reach_for(target=mug_id, arm=Arm.right)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])
replicant.grasp(target=mug_id, arm=Arm.right)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])
replicant.reset_arm(arm=[Arm.left, Arm.right])
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])
replicant.move_by(-4)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])
replicant.drop(arm=Arm.right)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])
c.communicate({"$type": "terminate"})
