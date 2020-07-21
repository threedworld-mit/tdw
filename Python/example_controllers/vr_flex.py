from tdw.controller import Controller
from tdw.output_data import FlexParticles


class VRFlex(Controller):
    """
    1. Create an Oculus VR rig.
    2. Create Flex-enabled objects.
    3. Receive Flex particle data.
    """

    def run(self):
        # Load the streamed scene and add controller rig.
        self.load_streamed_scene(scene="tdw_room_2018")

        # Create the container.
        self.communicate({"$type": "create_flex_container",
                          "collision_distance": 0.001,
                          "static_friction": 1.0,
                          "dynamic_friction": 1.0,
                          "iteration_count": 3,
                          "substep_count": 8,
                          "radius": 0.1875,
                          "damping": 0,
                          "drag": 0})

        self.communicate({"$type": "create_vr_rig"})

        # Add the table object.
        table_id = self.add_object("trunck",
                                   position={"x": 0, "y": 0, "z": 0.5})

        # Add the vase object and make it graspable.
        graspable_id_box = self.add_object("woven_box",
                                           position={"x": 0.2, "y": 1, "z": 0.5},
                                           library="models_core.json")

        self.communicate([{"$type": "set_kinematic_state",
                           "id": table_id,
                           "is_kinematic": True},
                          {"$type": "set_kinematic_state",
                           "id": graspable_id_box,
                           "is_kinematic": True}
                          ])

        # Assign the object a FlexActor.
        # Assign the object a Flex container.
        self.communicate([{"$type": "set_flex_solid_actor",
                           "id": graspable_id_box,
                           "mass_scale": 100.0,
                           "particle_spacing": 0.035},
                          {"$type": "assign_flex_container",
                           "id": graspable_id_box,
                           "container_id": 0}])

        self.communicate([{"$type": "set_flex_solid_actor",
                           "id": table_id,
                           "mass_scale": 120.0,
                           "particle_spacing": 0.035},
                          {"$type": "assign_flex_container",
                           "id": table_id,
                           "container_id": 0}])

        # Set the objects as graspable.
        self.communicate([{"$type": "set_graspable",
                           "id": table_id},
                          {"$type": "set_graspable",
                           "id": graspable_id_box}])
        
        # Send particles data for the box.
        resp = self.communicate({"$type": "send_flex_particles",
                                 "frequency": "always",
                                 "ids": [graspable_id_box]})

        while True:
            particles = FlexParticles(resp[0])
            for j in range(particles.get_num_objects()):
                # Print just the first five particles on the box.
                print(particles.get_particles(j)[:5])
            resp = self.communicate({"$type": "do_nothing"})


if __name__ == "__main__":
    VRFlex().run()
