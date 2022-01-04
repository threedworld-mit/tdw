from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.occupancy_map import OccupancyMap

"""
Minimal example of generating an occupancy map.
"""

c = Controller()
occupancy_map = OccupancyMap(cell_size=0.5)
c.add_ons.append(occupancy_map)
c.communicate([TDWUtils.create_empty_room(6, 6),
               c.get_add_object(model_name="trunck",
                                object_id=c.get_unique_id(),
                                position={"x": 0, "y": 0, "z": 1.5})])
occupancy_map.generate()
c.communicate([])
print(occupancy_map.occupancy_map)
c.communicate({"$type": "terminate"})
