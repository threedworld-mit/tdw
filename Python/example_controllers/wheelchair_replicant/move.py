from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.wheelchair_replicant import WheelchairReplicant
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.replicant.action_status import ActionStatus

"""
Move a WheelchairReplicant.
"""


def do_action():
    while replicant.action.status == ActionStatus.ongoing:
        c.communicate([])
    c.communicate([])


c = Controller()
replicant = WheelchairReplicant(position={"x": 0, "y": 0, "z": 2})
camera = ThirdPersonCamera(position={"x": 0.975, "y": 1.6, "z": -0.65},
                           look_at=replicant.replicant_id,
                           avatar_id="a")
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("wheelchair_replicant_move")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"],
                       path=path)
# Note the order in which the add-ons are added. The replicant needs to be first so that the camera can look at it.
c.add_ons.extend([replicant, camera, capture])
# Create the scene.
commands = [TDWUtils.create_empty_room(12, 12)]
object_id = Controller.get_unique_id()
commands.extend(Controller.get_add_physics_object(model_name="vase_02",
                                                  object_id=object_id,
                                                  position={"x": 3, "y": 0, "z": 1.5}))
c.communicate(commands)
# Move by a distance.
replicant.move_by(distance=2)
do_action()
# Move to an object.
replicant.move_to(target=object_id)
do_action()
# Move by a negative distance.
replicant.move_by(distance=-1.5)
do_action()
# Move to a position.
replicant.move_to(target={"x": 0, "y": 0, "z": 0.5})
do_action()
c.communicate({"$type": "terminate"})
