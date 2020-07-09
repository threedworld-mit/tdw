from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import AvatarKinematic


"""
A basic example of how to move a physics-enabled (non-kinematic) avatar.
"""


class AvatarMovement(Controller):
    A_ID = "a"

    def allow_movement(self):
        """
        Set the drag values to allow movement.
        """

        self.communicate({"$type": "set_avatar_drag",
                          "angular_drag": 5,
                          "avatar_id": self.A_ID,
                          "drag": 80})

    def run(self):
        a_id = "a"

        self.start()
        # Create an empty room.
        self.communicate(TDWUtils.create_empty_room(20, 20))

        self.communicate(TDWUtils.create_avatar(avatar_id=a_id,
                                                avatar_type="A_Img_Caps"))

        # Allow movement.
        self.allow_movement()

        # Receive transforms data.
        self.communicate({"$type": "send_avatars",
                          "frequency": "always"})

        moving = True
        # The number of frames so far that this avatar has turned.
        turn_count = 0

        for i in range(10000):
            # Move the avatar.
            if moving:
                resp = self.communicate({"$type": "move_avatar_forward_by",
                                         "avatar_id": a_id,
                                         "magnitude": 300})
            # Turn the avatar.
            else:
                resp = self.communicate({"$type": "turn_avatar_by",
                                         "avatar_id": a_id,
                                         "torque": 10})
                # Increment the turn counter.
                turn_count += 1

            # Get the transform data.
            t = AvatarKinematic(resp[0])
            x, y, z = t.get_position()
            # Get the avatar's distance from the center.
            d = TDWUtils.get_distance(TDWUtils.array_to_vector3([x, 0, z]), TDWUtils.VECTOR3_ZERO)

            # If the avatar is too far away from the center, turn it.
            if d > 4:
                if moving:
                    # Use a high drag value to stop the avatar.
                    self.communicate([{"$type": "set_avatar_drag",
                                       "angular_drag": 5,
                                       "avatar_id": a_id,
                                       "drag": 500}])
                    moving = False
                    turn_count = 0
                else:
                    if turn_count > 90:
                        moving = True
                        # Allow movement again.
                        self.allow_movement()


if __name__ == "__main__":
    AvatarMovement().run()
