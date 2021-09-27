from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.collision_manager import CollisionManager
from tdw.add_ons.object_manager import ObjectManager


class CollisionsAndFriction(Controller):
    """
    - Listen for collisions between objects.
    - Adjust the friction values of objects.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        # Add a collision manager and an object manager.
        self.collision_manager: CollisionManager = CollisionManager(enter=True, exit=True, stay=True, objects=True, environment=True)
        self.object_manager: ObjectManager = ObjectManager(transforms=False, rigidbodies=True, bounds=False)
        self.add_ons.extend([self.collision_manager, self.object_manager])

    def trial(self, fridge_dynamic_friction: float, fridge_static_friction: float, fridge_bounciness: float,
              chair_dynamic_friction: float, chair_static_friction: float, chair_bounciness: float) -> None:
        """
        Collide a chair with a fridge.

        :param fridge_dynamic_friction: The dynamic friction of the fridge.
        :param fridge_static_friction: The static friction of the fridge.
        :param fridge_bounciness: The bounciness of the fridge.
        :param chair_dynamic_friction: The dynamic friction of the chair.
        :param chair_static_friction: The static friction of the chair.
        :param chair_bounciness: The bounciness of the chair.
        """

        # Re-initialize the managers.
        self.collision_manager.initialized = False
        self.object_manager.initialized = False

        print("###\n\nNew Trial\n\n###\n")

        fridge_id = 0
        chair_id = 1

        # Destroy all objects currently in the scene.
        init_commands = [{"$type": "destroy_all_objects"}]
        # Create the avatar.
        init_commands.extend(TDWUtils.create_avatar(position={"x": 1, "y": 2.5, "z": 5},
                                                    look_at=TDWUtils.VECTOR3_ZERO))
        # Add the objects. Set the masses and physic materials.
        # Apply a force to the chair.
        init_commands.extend(self.get_add_physics_object(model_name="fridge_large",
                                                         object_id=fridge_id,
                                                         default_physics_values=False,
                                                         mass=40,
                                                         dynamic_friction=fridge_dynamic_friction,
                                                         static_friction=fridge_static_friction,
                                                         bounciness=fridge_bounciness))
        init_commands.extend(self.get_add_physics_object(model_name="chair_billiani_doll",
                                                         object_id=chair_id,
                                                         position={"x": 4, "y": 0, "z": 0},
                                                         default_physics_values=False,
                                                         mass=20,
                                                         dynamic_friction=chair_dynamic_friction,
                                                         static_friction=chair_static_friction,
                                                         bounciness=chair_bounciness))
        # Apply a force to the chair.
        init_commands.append({"$type": "apply_force_to_object",
                              "force": {"x": -200, "y": 0, "z": 0},
                              "id": chair_id})
        self.communicate(init_commands)

        # Iterate until the objects stop moving.
        done = False
        while not done:
            done = True
            # Check if all objects stopped moving.
            for object_id in self.object_manager.rigidbodies:
                if not self.object_manager.rigidbodies[object_id].sleeping:
                    done = False
                    break
            # Print collision data.
            for object_ids in self.collision_manager.obj_collisions:
                print(object_ids.int1, object_ids.int2, self.collision_manager.obj_collisions[object_ids].state,
                      self.collision_manager.obj_collisions[object_ids].relative_velocity)
                for normal, point in zip(self.collision_manager.obj_collisions[object_ids].normals,
                                         self.collision_manager.obj_collisions[object_ids].points):
                    print("\t", normal, point)
            for object_id in self.collision_manager.env_collisions:
                print(object_id, self.collision_manager.env_collisions[object_id].state,
                      self.collision_manager.env_collisions[object_id].floor)
                for normal, point in zip(self.collision_manager.env_collisions[object_id].normals,
                                         self.collision_manager.env_collisions[object_id].points):
                    print("\t", normal, point)
            # Advance 1 frame.
            self.communicate([])

    def run(self) -> None:
        """
        Do multiple trials and then quit.
        """

        # Create the room.
        self.communicate(TDWUtils.create_empty_room(12, 12))

        # Run a trial.
        self.trial(0.1, 0.12, 0.6, 0.8, 0.75, 0.1)

        # Run a trial with different friction and bounciness parameters.
        self.trial(0.9, 0.85, 1.0, 0.2, 0.75, 1.0)

        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    CollisionsAndFriction().run()
