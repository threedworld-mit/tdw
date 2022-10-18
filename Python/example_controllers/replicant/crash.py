from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.image_frequency import ImageFrequency
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


"""
Walk through, and collide with, an obstacle.
"""

c = Controller()
camera = ThirdPersonCamera(position={"x": -0.5, "y": 1.175, "z": 6},
                           look_at={"x": 0.5, "y": 1, "z": 0},
                           avatar_id="a")
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("replicant_crash")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"], path=path)
replicant = Replicant(position={"x": 0, "y": 0, "z": 4}, image_frequency=ImageFrequency.never)
# Don't try to avoid obstacles.
replicant.collision_detection.avoid = False
replicant.collision_detection.objects = False
# Append the add-ons.
c.add_ons.extend([replicant, camera, capture])
# Create a scene. Add a sofa. The sofa will be implausibly light.
commands = [TDWUtils.create_empty_room(12, 20),
            c.get_add_object(model_name="arflex_strips_sofa",
                             position={"x": 0, "y": 0, "z": 0},
                             object_id=Controller.get_unique_id())]
# Add the target object.
ball_id = Controller.get_unique_id()
commands.extend(c.get_add_physics_object(model_name="prim_sphere",
                                         object_id=ball_id,
                                         position={"x": 0, "y": 0, "z": -4.0},
                                         scale_factor={"x": 0.2, "y": 0.2, "z": 0.2},
                                         kinematic=True,
                                         gravity=False,
                                         library="models_special.json"))
# Send the commands.
c.communicate(commands)
replicant.move_to(target=ball_id)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])
c.communicate({"$type": "terminate"})
