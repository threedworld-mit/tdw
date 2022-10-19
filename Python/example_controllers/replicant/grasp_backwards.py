from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.add_ons.replicant import Replicant
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.arm import Arm
from tdw.replicant.image_frequency import ImageFrequency
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


c = Controller()
replicant = Replicant( position={"x": -4, "y": 0, "z": -2},
                       image_frequency=ImageFrequency.never)
camera = ThirdPersonCamera(position={"x": -1.5, "y": 1.175, "z": 5.25},
                           look_at={"x": 0.5, "y": 1, "z": 0},
                           avatar_id="a")
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("replicant_grasp_backwards")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"], path=path)
c.add_ons.extend([replicant, camera, capture])
basket_id = Controller.get_unique_id()
# Create a room and a basket.
commands = [TDWUtils.create_empty_room(12, 20),
            {"$type": "set_target_framerate",
             "framerate": 60}]
commands.extend(c.get_add_physics_object(model_name="basket_18inx18inx12iin_wicker",
                                         object_id=basket_id,
                                         position={"x": -0.8, "y": 0, "z": 2},
                                         rotation={"x": 0, "y": 110, "z": 0}))
c.communicate(commands)
# Walk to the basket.
replicant.move_to(target=basket_id, arrived_at=0.3)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])
# Turn backwards.
replicant.turn_by(180)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])
# Reach for the basket.
replicant.reach_for(target=basket_id, arm=Arm.right)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])
c.communicate({"$type": "terminate"})
