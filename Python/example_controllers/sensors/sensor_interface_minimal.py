from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.sensor_interface import SensorInterface
from tdw.sensors_data.analog_pin import AnalogPin
import time

"""
Minimal sensor interface example.
"""

c = Controller(launch_build=False)
sensor = SensorInterface()
c.add_ons.append(sensor)
c.communicate(TDWUtils.create_empty_room(12, 12))
while True:
    c.communicate({"$type": "analog_write",
                              "analog_pin": AnalogPin.A0.name,
                              "value": 1})
    time.sleep(0.5)
    c.communicate({"$type": "analog_write",
                              "analog_pin": AnalogPin.A0.name,
                              "value": 0})
    time.sleep(0.5)