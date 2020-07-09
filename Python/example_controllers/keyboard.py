from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from platform import system

if system() == "Windows":
    from msvcrt import getch
else:
    from getch import getch


"""
Use WASD or arrow keys to move an avatar.
"""


class KeyboardControls(Controller):
    def run(self, force=80):
        """
        :param force: The force magnitude used to move the avatar.
        """

        print("W, up-arrow = Move forward")
        print("S, down-arrow = Move backward")
        print("A, left-arrow = Turn counterclockwise")
        print("D, right-arrow = Turn clockwise")
        print("Esc = Quit")

        self.start()
        self.communicate(TDWUtils.create_empty_room(12, 12))
        self.communicate(TDWUtils.create_avatar(avatar_type="A_Img_Caps"))

        # Set high drag values so it doesn't feel like the avatar is sliding on ice.
        self.communicate({"$type": "set_avatar_drag",
                          "drag": 10,
                          "angular_drag": 20})

        # Change the floor material so it's easier to visualize the avatar's movement.
        self.communicate([self.get_add_material("parquet_alternating_orange", library="materials_high.json"),
                          {"$type": "set_proc_gen_floor_material",
                           "name": "parquet_alternating_orange"},
                          {"$type": "set_proc_gen_floor_texture_scale",
                           "scale": {"x": 8, "y": 8}}])

        done = False
        while not done:
            ch = getch()
            ch_int = ord(ch)
            forward = 0
            torque = 0
            # Move forward with w or up-arrow.
            if ch == b'w' or ch_int == 72:
                forward = force
            # Move backward with s or down-arrow.
            elif ch == b's' or ch_int == 80:
                forward = -force
            # Rotate counterclockwise with d or right-arrow.
            elif ch == b'd' or ch_int == 77:
                torque = force
            # Rotate clockwise with a or left-arrow.
            elif ch == b'a' or ch_int == 75:
                torque = -force
            # Quit with esc.
            elif ch_int == 27:
                done = True
                continue

            commands = []
            # If there was any directional input, apply a directional force.
            if abs(forward) > 0:
                commands.append({"$type": "move_avatar_forward_by",
                                 "magnitude": forward})
            # If there was any rotational input, apply a torque.
            if abs(torque) > 0:
                commands.append({"$type": "turn_avatar_by",
                                 "torque": torque})

            # If there was no input, do nothing and advance the simulation.
            # (This isn't necessary in this example, but you'll want this if anything else is moving in the scene).
            if len(commands) > 0:
                commands.append({"$type": "do_nothing"})

            self.communicate(commands)


KeyboardControls().run()
