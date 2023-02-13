from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.replicant.action_status import ActionStatus
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Collide with an obstacle.
"""

c = Controller()
camera = ThirdPersonCamera(position={"x": 3, "y": 1.175, "z": 2}, avatar_id="a")
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("replicant_crash")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"], path=path)
replicant = Replicant(position={"x": 0, "y": 0, "z": 0})
# Don't try to avoid obstacles.
replicant.collision_detection.avoid = False
replicant.collision_detection.objects = False
# Append the add-ons.
c.add_ons.extend([replicant, camera, capture])
# Create a scene. Add a sofa.
commands = [TDWUtils.create_empty_room(12, 20),
            Controller.get_add_object(model_name="arflex_strips_sofa",
                                      position={"x": 0, "y": 0, "z": 4},
                                      object_id=Controller.get_unique_id())]
# Send the commands.
c.communicate(commands)
camera.look_at(target=replicant.replicant_id)
replicant.move_by(8)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])
c.communicate([])
c.communicate({"$type": "terminate"})
