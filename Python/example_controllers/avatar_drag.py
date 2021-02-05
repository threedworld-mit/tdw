from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import AvatarSimpleBody

"""
Set the avatar's drag values to control its speed while in mid-air.
"""


class AvatarDrag(Controller):
    def run(self, drag_on_land, angular_drag_on_land):
        self.start()
        self.communicate(TDWUtils.create_empty_room(40, 40))

        # Create the avatar.
        self.communicate(TDWUtils.create_avatar(avatar_type="A_Simple_Body",
                                                position={"x": 0, "y": 1, "z": 0}))

        # When the y value of the avatar's position is this value, the avatar is on the ground.
        ground_y = 1
        # When the y value of the avatar's position exceeds ground_y by this much, it is in the air.
        in_air_threshold = 0.05

        # If true, the avatar is in the air.
        is_in_air = False

        # Set high default drag values.
        # Set a low mass.
        # Apply a force.
        # Request avatar data.
        resp = self.communicate([{"$type": "set_avatar_drag",
                                  "avatar_id": "a",
                                  "drag": 30,
                                  "angular_drag": 80},
                                 {"$type": "send_avatars",
                                  "frequency": "always"},
                                 {"$type": "apply_force_to_avatar",
                                  "avatar_id": "a",
                                  "direction": {"x": 0.3, "y": 0.7, "z": 0},
                                  "magnitude": 900}])

        for i in range(500):
            x, y, z = AvatarSimpleBody(resp[0]).get_position()
            # If the avatar just launched in to the air, set its drag values to 0.
            if y > ground_y + in_air_threshold and not is_in_air:
                is_in_air = True
                resp = self.communicate({"$type": "set_avatar_drag",
                                         "avatar_id": "a",
                                         "drag": 0,
                                         "angular_drag": 0})
                print("The avatar is in the air on frame: " + str(Controller.get_frame(resp[-1])))
            # If the avatar just landed on the ground, set drag values.
            elif y <= ground_y + in_air_threshold and is_in_air:
                resp = self.communicate({"$type": "set_avatar_drag",
                                         "avatar_id": "a",
                                         "drag": drag_on_land,
                                         "angular_drag": angular_drag_on_land})
                is_in_air = False
                print("The avatar is on the ground on frame: " + str(Controller.get_frame(resp[-1])))
            # Wait.
            else:
                resp = self.communicate({"$type": "do_nothing"})


if __name__ == "__main__":
    c = AvatarDrag()
    # Run a trial where the drag isn't reset when the avatar lands.
    c.run(0, 0)
    # Run a trial where high drag values are set when the avatar lands.
    c.run(80, 50)
