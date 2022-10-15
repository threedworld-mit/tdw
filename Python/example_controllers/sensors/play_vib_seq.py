from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.sensor_interface import SensorInterface
import time

"""
Minimal example of sending a custom command to an Arduino, to control 
a DRV2605 haptic motor controller. This will trigger a vibration pattern from 
a "pancake" haptic motor connected to the controller.
The command name "playSequence" is registered in the Arduino code using
this line:

uduino.addCommand("playSequence", playSeq);

When TDW sends the "playSequence" command, the function "playSeq" is invoked, 
which sends the requested vibration waveform to the haptic motor.
"""

c = Controller(launch_build=False)
sensor = SensorInterface()
c.add_ons.append(sensor)
c.communicate(TDWUtils.create_empty_room(12, 12))
while True:
    c.communicate(sensor.get_send_haptic_waveform_command(command_name="playSequence", wave_id=84))
    # Add a small delay between sends.
    for i in range(50):
        c.communicate([])
