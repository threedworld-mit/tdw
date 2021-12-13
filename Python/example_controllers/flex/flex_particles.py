from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, FlexParticles

"""
Minimal example of how to receive FlexParticle output data.
"""

c = Controller()
object_id = c.get_unique_id()
resp = c.communicate([TDWUtils.create_empty_room(12, 12),
                      {"$type": "convexify_proc_gen_room"},
                      {"$type": "create_flex_container"},
                      c.get_add_object(model_name="cube",
                                       library="models_flex.json",
                                       object_id=object_id),
                      {"$type": "set_flex_solid_actor",
                       "id": object_id,
                       "mass_scale": 5,
                       "particle_spacing": 0.125},
                      {"$type": "assign_flex_container",
                       "id": object_id,
                       "container_id": 0},
                      {"$type": "send_flex_particles"}])
for i in range(len(resp) - 1):
    r_id = OutputData.get_data_type_id(resp[i])
    if r_id == "flex":
        flex = FlexParticles(resp[i])
        for j in range(flex.get_num_objects()):
            print("Object ID", flex.get_id(j))
            print("Particles\n", flex.get_particles(j))
            print("Velocities\n", flex.get_velocities(j))
c.communicate({"$type": "terminate"})