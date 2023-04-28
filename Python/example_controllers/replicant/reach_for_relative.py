from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.arm import Arm
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Reach for a relative target.
"""

def do_action():
    while replicant.action.status == ActionStatus.ongoing:
        c.communicate([])
    c.communicate([])


c = Controller()
replicant = Replicant()
camera = ThirdPersonCamera(position={"x": 0, "y": 1.5, "z": 3.5},
                           look_at=replicant.replicant_id,
                           avatar_id="a")
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("replicant_reach_for_relative")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=[camera.avatar_id], path=path)
c.add_ons.extend([replicant, camera, capture])
for rotation in [0, 30, -45]:
    replicant.reset()
    camera.initialized = False
    capture.initialized = False
    c.communicate([{"$type": "load_scene",
                    "scene_name": "ProcGenScene"},
                   TDWUtils.create_empty_room(12, 12)])
    # Turn the Replicant.
    replicant.turn_by(rotation)
    do_action()
    # Reach for a relative target with the right hand.
    replicant.reach_for(target={"x": 0.6, "y": 1.5, "z": 0.3}, arm=Arm.right, absolute=False)
    do_action()
c.communicate({"$type": "terminate"})
