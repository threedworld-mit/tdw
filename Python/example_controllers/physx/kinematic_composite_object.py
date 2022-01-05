from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, CompositeObjects

"""
Make a composite object kinematic but make its sub-objects non-kinematic.
"""

c = Controller()
# Create the scene and add the object.
object_id = c.get_unique_id()
resp = c.communicate([TDWUtils.create_empty_room(12, 12),
                      c.get_add_object(model_name="b03_bosch_cbg675bs1b_2013__vray_composite",
                                       object_id=object_id),
                      {"$type": "send_composite_objects",
                       "frequency": "once"}])
# Get the composite object IDs. Assign each object a random color.
commands = []
for i in range(len(resp) - 1):
    r_id = OutputData.get_data_type_id(resp[i])
    if r_id == "comp":
        composite_objects = CompositeObjects(resp[i])
        for j in range(composite_objects.get_num()):
            if composite_objects.get_object_id(j) == object_id:
                # Make the root object kinematic.
                commands.append({"$type": "set_kinematic_state",
                                 "id": object_id,
                                 "is_kinematic": True,
                                 "use_gravity": False})
                # Make the sub-objects non-kinematic.
                for k in range(composite_objects.get_num_sub_objects(j)):
                    commands.append({"$type": "set_kinematic_state",
                                     "id": composite_objects.get_sub_object_id(j, k),
                                     "is_kinematic": False,
                                     "use_gravity": True})
c.communicate({"$type": "terminate"})