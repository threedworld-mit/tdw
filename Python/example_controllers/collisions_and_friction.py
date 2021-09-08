from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Collision, EnvironmentCollision


"""
- Listen for collisions between objects.
- Adjust the friction values of objects.
"""


class CollisionsAndFriction(Controller):
    def trial(self, d_f, s_f, b_f, d_c, s_c, b_c, collision_types):
        """
        Collide a chair with a fridge.

        :param d_f: The dynamic friction of the fridge.
        :param s_f: The static friction of the fridge.
        :param b_f: The bounciness of the fridge.
        :param d_c: The dynamic friction of the chair.
        :param s_c: The static friction of the chair.
        :param b_c: The bounciness of the chair.
        :param collision_types: The types of collisions to listen for.
        """

        print("###\n\nNew Trial\n\n###\n")

        fridge_id = 0
        chair_id = 1

        # Destroy all objects currently in the scene_data.
        init_commands = [{"$type": "destroy_all_objects"}]
        # Create the avatar.
        init_commands.extend(TDWUtils.create_avatar(position={"x": 1, "y": 2.5, "z": 5},
                                                    look_at=TDWUtils.VECTOR3_ZERO))
        # Add the objects.
        # Set the masses and physic materials.
        # Apply a force to the chair.
        # Receive collision data (note that by setting "stay" to True, you will receive a LOT of data;
        # see "Performance Optimizations" documentation.)
        init_commands.extend([self.get_add_object("fridge_large", object_id=fridge_id),
                              self.get_add_object("chair_billiani_doll", object_id=chair_id,
                                                  position={"x": 4, "y": 0, "z": 0}),
                              {"$type": "set_mass",
                               "id": fridge_id,
                               "mass": 40},
                              {"$type": "set_mass",
                               "id": chair_id,
                               "mass": 20},
                              {"$type": "set_physic_material",
                               "id": fridge_id,
                               "dynamic_friction": d_f,
                               "static_friction": s_f,
                               "bounciness": b_f},
                              {"$type": "set_physic_material",
                               "id": chair_id,
                               "dynamic_friction": d_c,
                               "static_friction": s_c,
                               "bounciness": b_c},
                              {"$type": "apply_force_to_object",
                               "force": {"x": -200, "y": 0, "z": 0},
                               "id": chair_id},
                              {"$type": "send_collisions",
                               "collision_types": collision_types,
                               "enter": True,
                               "exit": True,
                               "stay": True}])
        self.communicate(init_commands)

        # Iterate through 500 frames.
        # Every frame, listen for collisions, and parse the output data.
        for i in range(500):
            resp = self.communicate([])
            if len(resp) > 1:
                for r in resp[:-1]:
                    r_id = OutputData.get_data_type_id(r)
                    # There was a collision between two objects.
                    if r_id == "coll":
                        collision = Collision(r)
                        print("Collision between two objects:")
                        print("\tEvent: " + collision.get_state())
                        print("\tCollider: " + str(collision.get_collider_id()))
                        print("\tCollidee: " + str(collision.get_collidee_id()))
                        print("\tRelative velocity: " + str(collision.get_relative_velocity()))
                        print("\tContacts:")
                        for j in range(collision.get_num_contacts()):
                            print(str(collision.get_contact_normal(j)) + "\t" + str(collision.get_contact_point(j)))
                    # There was a collision between an object and the environment.
                    elif r_id == "enco":
                        collision = EnvironmentCollision(r)
                        print("Collision between an object and the environment:")
                        print("\tEvent: " + collision.get_state())
                        print("\tCollider: " + str(collision.get_object_id()))
                        print("\tContacts:")
                        for j in range(collision.get_num_contacts()):
                            print(str(collision.get_contact_normal(j)) + "\t" + str(collision.get_contact_point(j)))
                    else:
                        raise Exception(r_id)

    def run(self):
        self.start()

        # Create the room.
        self.communicate(TDWUtils.create_empty_room(12, 12))

        # Run a trial.
        self.trial(0.1, 0.12, 0.6, 0.8, 0.75, 0.1, ["obj"])

        # Run a trial with different friction and bounciness parameters.
        # Listen for environment collisions.
        self.trial(0.9, 0.85, 1.0, 0.2, 0.75, 1.0, ["obj", "env"])


if __name__ == "__main__":
    CollisionsAndFriction().run()
