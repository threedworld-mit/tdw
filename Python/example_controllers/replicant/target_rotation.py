from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.replicant.arm import Arm
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.add_ons.replicant import Replicant
from tdw.replicant.action_status import ActionStatus
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Reach for a chair twice. 
The first time, use the default target orientation. 
The second time, use the chair's rotation as the target rotation.
"""

c = Controller()
chair_id = Controller.get_unique_id()
for i, target_rotation in enumerate([None, chair_id]):
    # Clear the add-ons from the previous trial.
    c.add_ons.clear()
    replicant = Replicant()
    camera = ThirdPersonCamera(position={"x": -0.9, "y": 1.175, "z": 3},
                               look_at={"x": 0, "y": 1, "z": 0},
                               avatar_id="a")
    path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("replicant_target_rotation").joinpath(str(i))
    print(f"Images will be saved to: {path}")
    capture = ImageCapture(avatar_ids=["a"], path=path)
    c.add_ons.extend([replicant, camera, capture])
    c.communicate([{"$type": "load_scene",
                    "scene_name": "ProcGenScene"},
                   TDWUtils.create_empty_room(12, 12),
                   Controller.get_add_object(model_name="chair_billiani_doll",
                                             object_id=chair_id,
                                             position={"x": 0, "y": 0.6, "z": 1},
                                             rotation={"x": 70, "y": 45, "z": 2}),
                   {"$type": "step_physics",
                    "frames": 50}])
    # Reach for the chair.
    replicant.reach_for(target=chair_id, arm=Arm.right, rotations={Arm.right: chair_id})
    while replicant.action.status == ActionStatus.ongoing:
        c.communicate([])
    c.communicate([])
c.communicate({"$type": "terminate"})
