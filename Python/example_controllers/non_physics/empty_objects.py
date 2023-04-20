from tdw.add_ons.empty_object_manager import EmptyObjectManager
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

"""
Add an empty object to a cube and print its position per communicate() call.
"""

c = Controller()
object_id = 0
empty_object_manager = EmptyObjectManager(empty_object_positions={object_id: [{"x": 0, "y": 5, "z": 0}]})
c.add_ons.append(empty_object_manager)
c.communicate([TDWUtils.create_empty_room(12, 12),
               Controller.get_add_object(model_name="cube",
                                         object_id=object_id,
                                         library="models_flex.json",
                                         position={"x": 0, "y": 0.5, "z": 0},
                                         rotation={"x": 70, "y": 0, "z": 0})])
for i in range(10):
    c.communicate([])
    print(empty_object_manager.empty_objects[object_id][0])
c.communicate({"$type": "terminate"})
