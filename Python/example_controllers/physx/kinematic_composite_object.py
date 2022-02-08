from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.composite_object_manager import CompositeObjectManager
from tdw.output_data import OutputData, StaticRigidbodies

"""
Make a composite object kinematic but make its sub-objects non-kinematic.
"""

c = Controller()
composite_object_manager = CompositeObjectManager()
c.add_ons.append(composite_object_manager)
# Create the scene and add the object.
object_id = c.get_unique_id()
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="b03_bosch_cbg675bs1b_2013__vray_composite",
                                object_id=object_id)])
# Get the composite object IDs. Assign each object a random color.
commands = []
for object_id in composite_object_manager.static:
    # Make the root object kinematic.
    commands.append({"$type": "set_kinematic_state",
                     "id": object_id,
                     "is_kinematic": True,
                     "use_gravity": False})
    print("Object ID:", object_id)
    # Make all hinges non-kinematic.
    for sub_object_id in composite_object_manager.static[object_id].hinges:
        commands.append({"$type": "set_kinematic_state",
                         "id": sub_object_id,
                         "is_kinematic": False,
                         "use_gravity": True})
        print("Sub-object ID:", sub_object_id)
# Request static rigidbody data to confirm that the kinematic states were set.
commands.append({"$type": "send_static_rigidbodies"})
resp = c.communicate(commands)
kinematic = dict()
for i in range(len(resp) - 1):
    r_id = OutputData.get_data_type_id(resp[i])
    if r_id == "srig":
        srig = StaticRigidbodies(resp[i])
        for j in range(srig.get_num()):
            print(srig.get_id(j), srig.get_kinematic(j))
c.communicate({"$type": "terminate"})
