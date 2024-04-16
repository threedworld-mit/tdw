from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.fove_leap_motion import FoveLeapMotion
from tdw.output_data import OutputData, Fove
from tdw.add_ons.object_manager import ObjectManager

"""
Fove eye/hand calibration protocol.
"""

c = Controller(launch_build=False)
commands = [TDWUtils.create_empty_room(12, 12)]
vr = FoveLeapMotion(position={"x": 0, "y": 1, "z": 0}, time_step=0.01)
c.add_ons.append(vr)
om = ObjectManager()
c.add_ons.append(om)
c.communicate(commands)

while not vr.done:
    c.communicate([])
   
c.communicate({"$type": "terminate"})
