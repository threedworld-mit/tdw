import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Meshes, Rigidbodies, Bounds


class PerlinNoiseTerrain(Controller):
    """
    Generate Perlin noise terrain and roll a ball down the terrain.
    """

    def run(self) -> None:
        self.start()

        # Download visual materials into the simulation.
        # Generate Perlin noise terrain.
        terrain_material = "stone_mountain_grey"
        ball_material = "plastic_vinyl_glossy_yellow"
        resp = self.communicate([self.get_add_material(material_name=terrain_material),
                                 self.get_add_material(material_name=ball_material),
                                 {"$type": "perlin_noise_terrain",
                                  "size": {"x": 24, "y": 24},
                                  "subdivisions": 1,
                                  "turbulence": 1.75,
                                  "origin": {"x": 0.5, "y": 0.5},
                                  "visual_material": terrain_material,
                                  "texture_scale": {"x": 4, "y": 2},
                                  "dynamic_friction": 0.25,
                                  "static_friction": 0.4,
                                  "bounciness": 0.2,
                                  "max_y": 10}])

        # Read the mesh data of the terrain.
        # Get a good spot to place the object: The highest position near the center of the terrain mesh.
        object_position: np.array = np.array([0, 0, 0])
        origin: np.array = np.array([0, 0])
        distance = 6
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "mesh":
                meshes = Meshes(resp[i])
                vertices = meshes.get_vertices(0)
                for vertex in vertices:
                    if np.linalg.norm(np.array([vertex[0], vertex[2]]) - origin) > distance:
                        continue
                    if vertex[1] > object_position[1]:
                        object_position = vertex
        # Start the object above the vertex.
        object_position += 0.9

        # Add the ball. Set its visual material and physic material. Request output data.
        object_id = 0
        commands = [self.get_add_object(model_name="sphere",
                                        library="models_flex.json",
                                        position=TDWUtils.array_to_vector3(object_position),
                                        object_id=object_id),
                    {"$type": "set_visual_material",
                     "material_index": 0,
                     "material_name": ball_material,
                     "object_name": "sphere",
                     "id": object_id},
                    {"$type": "set_physic_material",
                     "dynamic_friction": 0.5,
                     "static_friction": 0.2,
                     "bounciness": 0.6,
                     "id": object_id},
                    {"$type": "send_bounds",
                     "frequency": "always"},
                    {"$type": "send_rigidbodies",
                     "frequency": "always"}]
        # Add a third-person camera.
        commands.extend(TDWUtils.create_avatar(position={"x": 12, "y": 6, "z": 12},
                                               look_at=object_id))
        resp = self.communicate(commands)

        # Run the simulation until either the ball stops moving or it falls off the edge of the terrain.
        done = False
        while not done:
            object_position: np.array = np.array([0, 0, 0])
            sleeping: bool = False
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                if r_id == "boun":
                    boun = Bounds(resp[i])
                    for j in range(boun.get_num()):
                        if boun.get_id(j) == object_id:
                            object_position = np.array(boun.get_center(j))
                elif r_id == "rigi":
                    rigi = Rigidbodies(resp[i])
                    for j in range(rigi.get_num()):
                        if rigi.get_id(j) == object_id:
                            sleeping = rigi.get_sleeping(j)
            done = object_position[1] < -0.1 or sleeping
            # Look at the ball.
            resp = self.communicate({"$type": "look_at",
                                     "object_id": object_id})
        # End the simulation.
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = PerlinNoiseTerrain(launch_build=False)
    c.run()
