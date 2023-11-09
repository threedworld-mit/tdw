from math import tan, radians
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.ui import UI
from tdw.add_ons.mouse import Mouse
from tdw.add_ons.ui_widgets.progress_bar import ProgressBar


class Progress(Controller):
    """
    Add a progress bar that increments every time you click an object until all objects have been clicked.
    """

    def run(self):
        # Clear all add-ons.
        self.add_ons.clear()
        field_of_view = 54
        avatar_z = -1.5
        # Add a camera and enable image capture.
        camera = ThirdPersonCamera(avatar_id="a",
                                   position={"x": 0, "y": 1.8, "z": avatar_z},
                                   field_of_view=field_of_view)
        # Add a UI add-on for the text.
        ui = UI()
        # Add UI text.
        ui.add_text(text="Click each cube",
                    font_size=24,
                    color={"r": 0, "g": 0, "b": 0, "a": 1},
                    position={"x": 0, "y": 0},
                    anchor={"x": 0, "y": 1},
                    pivot={"x": 0, "y": 1})
        # Add the progress bar. This is a subclass of UI that will automatically add a progress bar to the scene.
        progress_bar = ProgressBar(size={"x": 200, "y": 24})
        # Listen to the mouse.
        mouse = Mouse()
        self.add_ons.extend([camera, mouse, ui, progress_bar])
        num_objects = 5
        # Create the scene and add objects.
        commands = [TDWUtils.create_empty_room(12, 12)]
        object_z = 3
        # Get the initial x coordinate.
        x = -tan(radians(field_of_view / 2)) * (object_z + abs(avatar_z)) * 0.8
        dx = 2 * abs(x) / num_objects
        s = 0.3
        object_ids = []
        for i in range(num_objects):
            # Add an object.
            object_id = i
            commands.extend(Controller.get_add_physics_object(model_name="cube",
                                                              object_id=object_id,
                                                              library="models_flex.json",
                                                              position={"x": x, "y": 0, "z": object_z},
                                                              scale_factor={"x": s, "y": s, "z": s},
                                                              kinematic=True))
            object_ids.append(object_id)
            # Increment the x position.
            x += dx
        # Create the scene.
        self.communicate(commands)
        # Wait until all objects are clicked.
        clicked = list()
        while len(clicked) < len(object_ids):
            commands.clear()
            # The mouse is over an object, the mouse button is down, and the object hasn't been clicked yet.
            if mouse.mouse_is_over_object and mouse.left_button_pressed and mouse.mouse_over_object_id not in clicked:
                # Change the color of the cube.
                commands.append({"$type": "set_color",
                                 "id": mouse.mouse_over_object_id,
                                 "color": {"r": 1, "g": 0, "b": 0, "a": 1}})
                # Record the object as clicked.
                clicked.append(mouse.mouse_over_object_id)
                # Set the progress bar's value.
                progress_bar.set_value(len(clicked) / len(object_ids))
            # Continue the simulation.
            self.communicate(commands)
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = Progress()
    c.run()
