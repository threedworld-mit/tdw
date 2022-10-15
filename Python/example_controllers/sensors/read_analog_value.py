from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.sensor_interface import SensorInterface
from tdw.sensors_data.analog_pin import AnalogPin


"""
Minimal example of reading analog data back from an Arduino,
using a custom command.

"""

c = Controller(launch_build=False)
sensor = SensorInterface(board_type = "Arduino Leonardo")
c.add_ons.append(sensor)
c.communicate(TDWUtils.create_empty_room(12, 12))
while True:
    c.communicate({"$type": "read_analog_data",
                   "analog_pin": AnalogPin.A0.name})
    for i in range(10):
        c.communicate([])
