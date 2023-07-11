from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.wheelchair_replicant import WheelchairReplicant
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.replicant.action_status import ActionStatus

"""
Turn a WheelchairReplicant.
"""


def do_action():
    while replicant.action.status == ActionStatus.ongoing:
        c.communicate([])
    c.communicate([])


c = Controller()
replicant = WheelchairReplicant(position={"x": 0, "y": 0, "z": 0})
camera = ThirdPersonCamera(position={"x": -1.27, "y": 1.65, "z": -1.75},
                           look_at={"x": 1.5, "y": 0.5, "z": 1},
                           avatar_id="a")
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("wheelchair_replicant_turn")
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
# Turn by an angle.
replicant.turn_by(angle=-45)
do_action()
# Turn to a target object.
replicant.turn_to(target=object_id)
do_action()
# Turn to a target position.
replicant.turn_to(target={"x": -3, "y": 0, "z": -1})
do_action()
c.communicate({"$type": "terminate"})
