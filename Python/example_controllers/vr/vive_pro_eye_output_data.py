import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.vive_pro_eye import ViveProEye
from tdw.add_ons.ui import UI
from tdw.vr_data.vive_button import ViveButton
from tdw.output_data import OutputData, Raycast


class ViveProEyeOutputData(Controller):
    """
    An example of how to read the Vive Pro Eye output data.

    - Left trackpad click to apply a force to the cube.
    - Left reset click to quit.
    - Left and right trackpads to change the color of the cube.
    - Look at the cube to show a UI message.
    - Look around to move a marker showing the gaze position.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)

        # The color of the cube. This will be modified by controller axis events.
        self.color = {"r": 0, "g": 0, "b": 1, "a": 1}
        # Change the color of the cube at this rate.
        self.color_delta = 0.005
        # The ID of the cube.
        self.object_id = Controller.get_unique_id()
        # If True, we'll apply a force to the cube. This gets set in the left trackpad callback function.
        self.apply_force = False
        # If True, quit the simulation. This gets set in the left menu callback function.
        self.done = False

        # Initialize the Vive Pro Eye.
        self.vr = ViveProEye()
        # Do something on left/right axis movement.
        self.vr.listen_to_axis(is_left=True, function=self.left_axis)
        self.vr.listen_to_axis(is_left=False, function=self.right_axis)
        # Do something on button presses.
        self.vr.listen_to_button(button=ViveButton.left_trackpad_click, function=self.left_trackpad)
        self.vr.listen_to_button(button=ViveButton.left_menu, function=self.quit)

        # The `UI` add-on is used to show text if the user is looking at the cube.
        self.ui = UI()
        self.ui.attach_canvas_to_vr_rig()
        self.text_id = self.ui.add_text(text="",
                                        font_size=36,
                                        position={"x": 0, "y": 0},
                                        color={"r": 1, "g": 0, "b": 0, "a": 1},
                                        raycast_target=False)
        self.add_ons.extend([self.vr, self.ui])

    def left_axis(self, axis: np.ndarray):
        # Adjust the cube's color.
        # Notice that we aren't sending a command.
        # This will tell the controller in `run()` to send the relevant command.
        if axis[0] > 0:
            self.color_up("r")
        elif axis[0] < 0:
            self.color_down("r")
        if axis[1] > 0:
            self.color_up("g")
        elif axis[1] < 0:
            self.color_down("g")

    def right_axis(self, axis: np.ndarray):
        # Adjust the cube's color.
        # Notice that we aren't sending a command.
        # This will tell the controller in `run()` to send the relevant command.
        if axis[0] > 0:
            self.color_up("b")
        elif axis[0] < 0:
            self.color_down("b")
        if axis[1] > 0:
            self.color_up("a")
        elif axis[1] < 0:
            self.color_down("a")

    def left_trackpad(self):
        # When the left trackpad is clicked, apply force.
        # Notice that we aren't actually sending a command.
        # This will tell the controller in `run()` to send the relevant command.
        self.apply_force = True

    def quit(self):
        # Quit the simulation.
        # Notice that we aren't sending a command.
        # This will tell the controller in `run()` to send the relevant command.
        self.done = True

    def color_up(self, channel: str):
        self.color[channel] += self.color_delta
        if self.color[channel] > 1:
            self.color[channel] = 1

    def color_down(self, channel: str):
        self.color[channel] -= self.color_delta
        if self.color[channel] < 0:
            self.color[channel] = 0

    def run(self):
        resp = self.communicate([TDWUtils.create_empty_room(12, 12),
                                 Controller.get_add_object(model_name="cube",
                                                           library="models_flex.json",
                                                           object_id=self.object_id,
                                                           position={"x": 0, "y": 0, "z": 0.5}),
                                 {"$type": "scale_object",
                                  "id": self.object_id,
                                  "scale_factor": {"x": 0.2, "y": 0.2, "z": 0.2}}])
        while not self.done:
            # Set the color of the cube.
            commands = [{"$type": "set_color",
                         "id": self.object_id,
                         "color": self.color}]
            # Apply a force to the cube.
            if self.apply_force:
                self.apply_force = False
                commands.append({"$type": "apply_force_to_object",
                                 "force": {"x": 0.25, "y": 0, "z": 0},
                                 "id": self.object_id})
            if self.object_id in self.vr.focused_objects:
                self.ui.set_text(text="I can see the object", ui_id=self.text_id)
            else:
                self.ui.set_text(text="", ui_id=self.text_id)
            # If we have eye tracking data, raycast along the eye ray.
            if self.vr.world_eye_data.valid:
                origin = self.vr.world_eye_data.ray[0]
                direction = self.vr.world_eye_data.ray[1]
                destination = origin + direction * 20
                commands.append({"$type": "send_raycast",
                                 "id": 0,
                                 "origin": TDWUtils.array_to_vector3(origin),
                                 "destination": TDWUtils.array_to_vector3(destination)})
            # If there was a raycast, add a position marker.
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                if r_id == "rayc":
                    raycast = Raycast(resp[i])
                    if raycast.get_hit():
                        point = raycast.get_point()
                        commands.extend([{"$type": "remove_position_markers"},
                                         {"$type": "add_position_marker",
                                          "position": {"x": point[0], "y": point[1], "z": point[2]}}])
            resp = self.communicate(commands)
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = ViveProEyeOutputData()
    c.run()
