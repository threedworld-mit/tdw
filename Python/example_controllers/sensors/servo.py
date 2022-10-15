from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.sensor_interface import SensorInterface
from tdw.sensors_data.analog_pin import AnalogPin
from tdw.sensors_data.pin_mode import PinMode
import time
from random import uniform

"""
Minimal example of controlling a servo motor from TDW.
"""

c = Controller(launch_build=False)
sensor = SensorInterface()
c.add_ons.append(sensor)
c.communicate(TDWUtils.create_empty_room(12, 12))

servo_pin = 5
servo_angle = 0
max_servo_angle = 180

while True:
    # Randomly rotate the servo, with a delay between rotations.
    servo_angle = int(uniform(30, max_servo_angle))
    command = sensor.get_analog_servo_write_command(servo_pin, servo_angle)
    c.communicate(command)
    for i in range(100):
        c.communicate([])
	