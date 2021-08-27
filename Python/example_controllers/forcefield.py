from tdw.controller import Controller
from tdw.output_data import Transforms
from tdw.tdw_utils import TDWUtils
from tdw.librarian import ModelLibrarian
import numpy as np


"""
Simulate a "forcefield" that objects will bounce off of.
"""


class ForceField(Controller):
    def run(self):
        rng = np.random.RandomState(0)
        self.model_librarian = ModelLibrarian("models_special.json")
        self.start()
        commands = [TDWUtils.create_empty_room(100, 100)]

        # The starting height of the objects.
        y = 10
        # The radius of the circle of objects.
        r = 7.0
        # The mass of each object.
        mass = 5

        # Get all points within the circle defined by the radius.
        p0 = np.array((0, 0))
        o_id = 0
        for x in np.arange(-r, r, 1):
            for z in np.arange(-r, r, 1):
                p1 = np.array((x, z))
                dist = np.linalg.norm(p0 - p1)
                if dist < r:
                    # Add an object.
                    # Set its mass, physics properties, and color.
                    commands.extend([self.get_add_object("prim_cone",
                                                         object_id=o_id,
                                                         position={"x": x, "y": y, "z": z},
                                                         rotation={"x": 0, "y": 0, "z": 180}),
                                     {"$type": "set_mass",
                                      "id": o_id,
                                      "mass": mass},
                                     {"$type": "set_physic_material",
                                      "dynamic_friction": 0.8,
                                      "static_friction": 0.7,
                                      "bounciness": 0.5,
                                      "id": o_id},
                                     {"$type": "set_color",
                                      "color": {"r": rng.random_sample(),
                                                "g": rng.random_sample(),
                                                "b": rng.random_sample(),
                                                "a": 1.0},
                                      "id": o_id}])
                    o_id += 1
        # Request transforms per frame.
        commands.extend([{"$type": "send_transforms",
                          "frequency": "always"}])
        # Create an avatar to observe the grisly spectacle.
        avatar_position = {"x": -20, "y": 8, "z": 18}
        commands.extend(TDWUtils.create_avatar(position=avatar_position, look_at=TDWUtils.VECTOR3_ZERO))
        commands.append({"$type": "set_focus_distance",
                         "focus_distance": TDWUtils.get_distance(avatar_position, TDWUtils.VECTOR3_ZERO)})
        resp = self.communicate(commands)

        # If an objects are this far away from (0, 0, 0) the forcefield "activates".
        forcefield_radius = 5
        # The forcefield will bounce objects away at this force.
        forcefield_force = -10
        zeros = np.array((0, 0, 0))
        for i in range(1000):
            transforms = Transforms(resp[0])
            commands = []
            for j in range(transforms.get_num()):
                pos = transforms.get_position(j)
                pos = np.array(pos)
                # If the object is in the forcefield, apply a force.
                if TDWUtils.get_distance(TDWUtils.array_to_vector3(pos), TDWUtils.VECTOR3_ZERO) <= forcefield_radius:
                    # Get the normalized directional vector and multiply it by the force magnitude.
                    d = zeros - pos
                    d = d / np.linalg.norm(d)
                    d = d * forcefield_force
                    commands.append({"$type": "apply_force_to_object",
                                     "id": transforms.get_id(j),
                                     "force": TDWUtils.array_to_vector3(d)})
            resp = self.communicate(commands)


if __name__ == "__main__":
    ForceField().run()
