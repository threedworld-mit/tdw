from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

"""
Using NVIDIA Flex, drape a cloth over an object.
"""


class ClothDrape(Controller):
    def run(self):
        # Load a nice-looking room.
        self.load_streamed_scene(scene="tdw_room_2018")

        # Create the Flex container.
        self.communicate({"$type": "create_flex_container",
                          "collision_distance": 0.001,
                          "static_friction": 1.0,
                          "dynamic_friction": 1.0,
                          "iteration_count": 5,
                          "substep_count": 8,
                          "radius": 0.1875,
                          "damping": 0,
                          "drag": 0})

        # Create the avatar.
        # Teleport the avatar.
        # Look at the target position.
        self.communicate(TDWUtils.create_avatar(position={"x": 2.0, "y": 1, "z": 1},
                                                look_at={"x": -1.2, "y": 0.5, "z": 0}))

        # Create the solid object.
        solid_id = self.add_object("linbrazil_diz_armchair",
                                   position={"x": -1.2, "y": 0, "z": 0},
                                   rotation={"x": 0.0, "y": 90, "z": 0.0},
                                   library="models_core.json")
        # Make the object kinematic.
        self.communicate({"$type": "set_kinematic_state",
                          "id": solid_id})
        # Assign the object a FlexActor.
        # Assign the object a Flex container.
        self.communicate([{"$type": "set_flex_solid_actor",
                           "id": solid_id,
                           "mass_scale": 100.0,
                           "particle_spacing": 0.035},
                          {"$type": "assign_flex_container",
                           "id": solid_id,
                           "container_id": 0}])

        # Create the cloth.
        cloth_id = self.add_object("cloth_square",
                                   position={"x": -1.2, "y": 1.0, "z": 0},
                                   library="models_special.json")
        # Make the cloth kinematic.
        self.communicate({"$type": "set_kinematic_state",
                          "id": cloth_id})
        # Assign the cloth a FlexActor.
        # Assign the cloth a Flex container.
        self.communicate([{"$type": "set_flex_cloth_actor",
                           "id": cloth_id,
                           "mass_scale": 1,
                           "mesh_tesselation": 1,
                           "tether_stiffness": 0.5,
                           "bend_stiffness": 1.0,
                           "self_collide": False,
                           "stretch_stiffness": 1.0},
                          {"$type": "assign_flex_container",
                           "id": cloth_id,
                           "container_id": 0}
                          ])

        # Iterate for 500 frames.
        for i in range(500):
            self.communicate([])


if __name__ == "__main__":
    ClothDrape().run()
