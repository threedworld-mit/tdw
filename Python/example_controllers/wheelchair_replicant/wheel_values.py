from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.wheelchair_replicant import WheelchairReplicant
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.replicant.action_status import ActionStatus
from tdw.wheelchair_replicant.wheel_values import WheelValues

"""
Turn and move with explicit wheel values.
"""


def do_action():
    while replicant.action.status == ActionStatus.ongoing:
        c.communicate([])
    c.communicate([])


c = Controller()
replicant = WheelchairReplicant(position={"x": 0, "y": 0, "z": 0})
camera = ThirdPersonCamera(position={"x": -2, "y": 2, "z": -1.75},
                           look_at=replicant.replicant_id,
                           avatar_id="a")
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("wheelchair_replicant_wheel_values")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"],
                       path=path)
c.add_ons.extend([replicant, camera, capture])
c.communicate(TDWUtils.create_empty_room(12, 12))
# Turn by an angle using default wheel values.
replicant.turn_by(angle=-45)
do_action()
# Turn by an angle using custom wheel values.
angle = 45
replicant.turn_by(angle=angle, wheel_values=WheelValues(brake_at=angle - 1,
                                                        brake_torque=5,
                                                        left_motor_torque=20,
                                                        right_motor_torque=-5,
                                                        steer_angle=angle))
do_action()
# Move by a distance using default wheel values.
distance = 1.5
replicant.move_by(distance=distance)
do_action()
# Move by a distance using custom wheel values.
replicant.move_by(distance=distance, wheel_values=WheelValues(brake_at=distance - 0.25,
                                                              brake_torque=5,
                                                              left_motor_torque=2,
                                                              right_motor_torque=2,
                                                              steer_angle=0))
do_action()
c.communicate({"$type": "terminate"})
