from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.replicant.action_status import ActionStatus

"""
Move a Replicant by a target distance and print its status.
"""

c = Controller()
replicant = Replicant(position={"x": 0, "y": 0, "z": 2})
camera = ThirdPersonCamera(position={"x": 2, "y": 1.6, "z": 1},
                           look_at=replicant.replicant_id,
                           avatar_id="a")
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("move_by")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"],
                       path=path)
# Note the order in which the add-ons are added. The replicant needs to be first so that the camera can look at it.
c.add_ons.extend([replicant, camera, capture])
# Create the scene. Set the framerate.
c.communicate(TDWUtils.create_empty_room(12, 12))
# Start walking.
replicant.move_by(2)
# Continue walking until the action ends.
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])
print(replicant.action.status)
c.communicate({"$type": "terminate"})
