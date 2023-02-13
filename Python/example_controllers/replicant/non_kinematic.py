from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.replicant.action_status import ActionStatus

"""
Move a Replicant through a kinematic object and a wall.
"""

c = Controller()
replicant = Replicant()
camera = ThirdPersonCamera(position={"x": 2, "y": 1.6, "z": 1},
                           look_at=replicant.replicant_id,
                           avatar_id="a")
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("replicant_non_kinematic")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"],
                       path=path)
c.add_ons.extend([replicant, camera, capture])
# Create the scene.
commands = [TDWUtils.create_empty_room(12, 12)]
# Add a kinematic object to the scene.
commands.extend(Controller.get_add_physics_object(model_name="trunck",
                                                  object_id=Controller.get_unique_id(),
                                                  position={"x": 0, "y": 0, "z": 3},
                                                  kinematic=True))
c.communicate(commands)
# Look at the Replicant.
camera.look_at(replicant.replicant_id)
# Disable obstacle avoidance.
replicant.collision_detection.avoid = False
# Disable checks for object collisions.
replicant.collision_detection.objects = False
# Start walking.
replicant.move_by(20)
# Continue walking until the action ends.
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])
c.communicate([])
c.communicate({"$type": "terminate"})
