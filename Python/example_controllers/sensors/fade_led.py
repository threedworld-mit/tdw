from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.sensor_interface import SensorInterface
from tdw.sensors_data.analog_pin import AnalogPin
from tdw.sensors_data.pin_mode import PinMode
import time

"""
Minimal sensor interface example.
"""

c = Controller(launch_build=False)
sensor = SensorInterface(board_type = "Arduino Leonardo")
c.add_ons.append(sensor)
c.communicate(TDWUtils.create_empty_room(12, 12))

led_pin = 11
brightness = 0
fade_amount = 5

while True:
    command = sensor.get_analog_pwm_write_command(led_pin, brightness)
    c.communicate(command)
    brightness += fade_amount;
    if brightness <= 0 or brightness >= 255:
        fade_amount = -fade_amount;
    for i in range(10):
        c.communicate([])
	