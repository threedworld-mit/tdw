from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.object_manager import ObjectManager


"""
This is very similar to object_output_data.py except that it uses an ObjectManager add-on.
"""

c = Controller()
om = ObjectManager(transforms=True, rigidbodies=True, bounds=False)
c.add_ons.append(om)

# Send the commands.
resp = c.communicate([TDWUtils.create_empty_room(12, 12),
                      c.get_add_object(model_name="iron_box",
                                       position={"x": 0, "y": 6, "z": 0},
                                       rotation={"x": 25, "y": 38, "z": -10},
                                       object_id=c.get_unique_id())])

# Print the name and category of each object.
for object_id in om.objects_static:
    print(object_id, om.objects_static[object_id].name, om.objects_static[object_id].category)

# Run the simulation until all objects stop moving.
positions = dict()
sleeping = False
while not sleeping:
    sleeping = True
    for object_id in om.rigidbodies:
        if not om.rigidbodies[object_id].sleeping:
            sleeping = False
    # Remember the position
    for object_id in om.transforms:
        if object_id not in positions:
            positions[object_id] = list()
        positions[object_id].append(om.transforms[object_id].position)
    # Advance once frame.
    c.communicate([])
print(positions)
c.communicate({"$type": "terminate"})
