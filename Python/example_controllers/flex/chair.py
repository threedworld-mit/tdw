from tdw.controller import Controller
from tdw.output_data import OutputData, FlexParticles
from tdw.tdw_utils import TDWUtils


"""
Create a soft-body chair with the NVIDIA Flex physics engine.
"""

c = Controller()
# Load a scene. Create a Flex container. Add a chair. Make the chair a soft-body actor.
# Request particle data.
object_id = c.get_unique_id()
commands = [c.get_add_scene(scene_name="tdw_room"),
            {"$type": "set_time_step",
             "time_step": 0.02},
            {"$type": "create_flex_container",
             "particle_size": 0.1,
             "collision_distance": 0.025,
             "solid_rest": 0.1},
            c.get_add_object(model_name="linbrazil_diz_armchair",
                             object_id=object_id,
                             position={"x": 0.0, "y": 2.0, "z": 0.0},
                             rotation={"x": 25.0, "y": 45.0, "z": -40.0},
                             library="models_core.json"),
            {"$type": "set_flex_soft_actor",
             "id": object_id,
             "skinning_falloff": 0.5,
             "volume_sampling": 1.0,
             "mass_scale": 1.0,
             "cluster_stiffness": 0.2,
             "cluster_spacing": 0.2,
             "cluster_radius": 0.2,
             "link_radius": 0,
             "link_stiffness": 1.0,
             "particle_spacing": 0.025},
            {"$type": "assign_flex_container",
             "id": object_id,
             "container_id": 0},
            {"$type": "send_flex_particles",
             "frequency": "always"}]
commands.extend(TDWUtils.create_avatar(position={"x": -1.5, "y": 0.85, "z": -0.5}))
commands.append({"$type": "look_at",
                 "object_id": object_id,
                 "use_centroid": True})
resp = c.communicate(commands)
for i in range(100):
    for j in range(len(resp) - 1):
        r_id = OutputData.get_data_type_id(resp[j])
        if r_id == "flex":
            # Output example data.
            particles = FlexParticles(resp[j])
            for k in range(particles.get_num_objects()):
                print(particles.get_id(k))
                print(particles.get_velocities(k))
                print(particles.get_particles(k))
    # Look at the object.
    resp = c.communicate({"$type": "look_at",
                          "object_id": object_id,
                          "use_centroid": True})
c.communicate({"$type": "terminate"})
