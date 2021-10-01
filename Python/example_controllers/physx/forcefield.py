from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.object_manager import ObjectManager
import numpy as np


class ForceField(Controller):
    """
    Simulate a "forcefield" that objects will bounce off of.
    """

    def run(self) -> None:
        rng = np.random.RandomState(0)
        commands = [TDWUtils.create_empty_room(100, 100)]

        # The starting height of the objects.
        y = 10
        # The radius of the circle of objects.
        r = 7.0
        origin = np.array([0, 0, 0])
        # Get all points within the circle defined by the radius.
        p0 = np.array((0, 0))
        o_id = 0
        for x in np.arange(-r, r, 1):
            for z in np.arange(-r, r, 1):
                p1 = np.array((x, z))
                dist = np.linalg.norm(p0 - p1)
                if dist < r:
                    # Add an object. Set its physics properties.
                    commands.extend(self.get_add_physics_object(model_name="prim_cone",
                                                                library="models_special.json",
                                                                object_id=o_id,
                                                                position={"x": x, "y": y, "z": z},
                                                                rotation={"x": 0, "y": 0, "z": 180},
                                                                default_physics_values=False,
                                                                mass=5,
                                                                dynamic_friction=0.8,
                                                                static_friction=0.7,
                                                                bounciness=0.5))
                    # Set a random color.
                    commands.append({"$type": "set_color",
                                     "color": {"r": rng.random_sample(),
                                               "g": rng.random_sample(),
                                               "b": rng.random_sample(),
                                               "a": 1.0},
                                     "id": o_id})
                    o_id += 1
                    print(o_id)
        # Add an object manager.
        object_manager = ObjectManager(transforms=True, rigidbodies=False, bounds=False)
        # Create a camera to observe the grisly spectacle.
        avatar_position = {"x": -20, "y": 8, "z": 18}
        camera = ThirdPersonCamera(position=avatar_position,
                                   avatar_id="a",
                                   look_at=TDWUtils.VECTOR3_ZERO)
        self.add_ons.extend([object_manager, camera])
        commands.append({"$type": "set_focus_distance",
                         "focus_distance": np.linalg.norm(TDWUtils.vector3_to_array(avatar_position) - origin)})
        self.communicate(commands)
        # If an objects are this far away from (0, 0, 0) the forcefield "activates".
        forcefield_radius = 5
        # The forcefield will bounce objects away at this force.
        forcefield_force = -10
        zeros = np.array((0, 0, 0))
        for i in range(1000):
            commands = []
            for object_id in object_manager.transforms:
                # If the object is in the forcefield, apply a force.
                if np.linalg.norm(object_manager.transforms[object_id].position - origin) <= forcefield_radius:
                    # Get the normalized directional vector and multiply it by the force magnitude.
                    d = zeros - object_manager.transforms[object_id].position
                    d = d / np.linalg.norm(d)
                    d = d * forcefield_force
                    commands.append({"$type": "apply_force_to_object",
                                     "id": object_id,
                                     "force": TDWUtils.array_to_vector3(d)})
            self.communicate(commands)
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    ForceField().run()
