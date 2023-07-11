from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.wheelchair_replicant import WheelchairReplicant
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.arm import Arm
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Reach for a target object.
"""

c = Controller()
replicant = WheelchairReplicant()
camera = ThirdPersonCamera(position={"x": 0, "y": 1.5, "z": 2.5},
                           look_at=replicant.replicant_id,
                           avatar_id="a")
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("wheelchair_replicant_reach_for_object")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=[camera.avatar_id], path=path)
c.add_ons.extend([replicant, camera, capture])
# Set the object ID.
object_id = Controller.get_unique_id()
commands = [TDWUtils.create_empty_room(12, 12)]
# Add a table and a coffee mug.
commands.extend(Controller.get_add_physics_object(model_name="side_table_wood",
                                                  object_id=Controller.get_unique_id(),
                                                  position={"x": 0.72, "y": 0, "z": 0.1},
                                                  rotation={"x": 0, "y": 90, "z": 0},
                                                  kinematic=True))
commands.extend(Controller.get_add_physics_object(model_name="coffeemug",
                                                  object_id=object_id,
                                                  position={"x": 0.6, "y": 0.6108887, "z": 0.18}))
c.communicate(commands)
# Reach for the mug.
replicant.reach_for(target=object_id, arm=Arm.right)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])
c.communicate([])
c.communicate({"$type": "terminate"})
