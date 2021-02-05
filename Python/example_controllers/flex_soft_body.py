from tdw.controller import Controller
from tdw.output_data import FlexParticles
from tdw.tdw_utils import TDWUtils


"""
Create a soft-body object with the NVIDIA Flex physics engine.
"""


class FlexSoftBody(Controller):
    def run(self):
        self.load_streamed_scene(scene="tdw_room")

        self.communicate({"$type": "set_time_step", "time_step": 0.02})

        # Create the container.
        self.communicate({"$type": "create_flex_container",
                          "particle_size": 0.1,
                          "collision_distance": 0.025,
                          "solid_rest": 0.1})

        # Create the avatar.
        self.communicate(TDWUtils.create_avatar(position={"x": -1.5, "y": 0.85, "z": -0.5}))

        # Add the object.
        object_id = self.add_object("linbrazil_diz_armchair",
                                    position={"x": 0.0, "y": 2.0, "z": 0.0},
                                    rotation={"x": 25.0, "y": 45.0, "z": -40.0},
                                    library="models_core.json")

        # Set the object to kinematic.
        # Set the soft actor.
        # Assign the actor's container.
        self.communicate([{"$type": "set_kinematic_state",
                           "id": object_id},
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
                           "container_id": 0}
                          ])

        # Send particles data.
        resp = self.communicate([{"$type": "send_flex_particles",
                                 "frequency": "always"}])

        # Output example data.
        particles = FlexParticles(resp[0])
        for j in range(particles.get_num_objects()):
            print(particles.get_id(j))
            print(particles.get_velocities(j))
            print(particles.get_particles(j))

        for i in range(1000):
            # Look at the object.
            self.communicate({"$type": "look_at",
                              "avatar_id": "a",
                              "object_id": object_id,
                              "use_centroid": True})


if __name__ == "__main__":
    FlexSoftBody().run()
