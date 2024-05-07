from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.fove_leap_motion import FoveLeapMotion
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.add_ons.object_manager import ObjectManager
from tdw.vr_data.fove.calibration_state import CalibrationState

"""
A minimal FOVE leap motion controller.
"""

c = Controller()
commands = [TDWUtils.create_empty_room(12, 12)]
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("fove_scene/calibration_data_")
print(f"Calibration data will be saved to: {path.parent}")
fove = FoveLeapMotion(position={"x": 0, "y": 1.0, "z": 0},
                      rotation=180.0,
                      attach_avatar=False,
                      time_step=0.01,
                      allow_headset_movement=False,
                      allow_headset_rotation=False,
                      calibration_data_path=str(path.resolve()),
                      timestamp=True)
c.add_ons.append(fove)
om = ObjectManager()
c.add_ons.append(om)
c.communicate(commands)

while not fove.done:
    # Test if calibration done.
    if fove.calibration_state == CalibrationState.running:
        fove.initialize_scene()
    c.communicate([])
   
c.communicate({"$type": "terminate"})
