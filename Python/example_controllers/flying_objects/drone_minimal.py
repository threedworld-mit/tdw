from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.drone import Drone

"""
Minimal drone  example.
"""

c = Controller(launch_build=False)
drone = Drone()
c.add_ons.append(drone)
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="rh10",
                                object_id=Controller.get_unique_id(),
                                position={"x": 0, "y": 0, "z": 0.5})])
for i in range(200):
    c.communicate([])

