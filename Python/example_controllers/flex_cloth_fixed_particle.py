import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, FlexParticles

"""
Create a Flex cloth object and "fix" one of its corners in mid-air.
"""


class FlexClothFixedParticle(Controller):
    def run(self):
        o_id = 0
        self.start()
        # 1. Create a room.
        # 2. Create a Flex container.
        # 3. Add a cloth object and set the cloth actor.
        # 4. Request Flex particle output data (this frame only).
        commands = [TDWUtils.create_empty_room(12, 12),
                    {"$type": "create_flex_container",
                     "collision_distance": 0.001,
                     "static_friction": 1.0,
                     "dynamic_friction": 1.0,
                     "iteration_count": 12,
                     "substep_count": 12,
                     "radius": 0.1875,
                     "damping": 0,
                     "drag": 0},
                    self.get_add_object("cloth_square",
                                        library="models_special.json",
                                        position={"x": 0, "y": 2, "z": 0},
                                        rotation={"x": 0, "y": 0, "z": 0},
                                        object_id=o_id),
                    {"$type": "set_flex_cloth_actor",
                     "id": o_id,
                     "mesh_tesselation": 1,
                     "stretch_stiffness": 0.5620341548096974,
                     "bend_stiffness": 0.6528988964052056,
                     "tether_stiffness": 0.7984931184979334,
                     "tether_give": 0,
                     "pressure": 0,
                     "mass_scale": 1},
                    {"$type": "assign_flex_container",
                     "container_id": 0,
                     "id": o_id},
                    {"$type": "send_flex_particles",
                     "frequency": "once"}]
        # Add to the list of commands: create the avatar, teleport it to a position, look at a position.
        commands.extend(TDWUtils.create_avatar(position={"x": -2.75, "y": 2.3, "z": -2},
                                               look_at={"x": 0, "y": 0.25, "z": 0}))
        # Send the commands.
        resp = self.communicate(commands)

        for r in resp[:-1]:
            r_id = OutputData.get_data_type_id(r)
            # This is FlexParticles data.
            if r_id == "flex":
                fp = FlexParticles(resp[0])
                # The maximum distance between a particle and the center of the cloth.
                max_d = 0
                # The ID of the particle at the maximum distance.
                max_id = 0
                p_id = 0
                for p in fp.get_particles(0):
                    # Get the particle that is furthest from the center.
                    d = np.linalg.norm(p[:-1] - 1)
                    if d > max_d:
                        max_d = d
                        max_id = p_id
                    p_id += 1
                # Set the particle as "fixed".
                self.communicate({"$type": "set_flex_particle_fixed",
                                  "is_fixed": True,
                                  "particle_id": max_id,
                                  "id": o_id})

            for i in range(800):
                self.communicate([])


if __name__ == "__main__":
    FlexClothFixedParticle().run()
