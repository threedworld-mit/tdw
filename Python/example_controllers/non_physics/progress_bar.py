from tdw.controller import Controller
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.add_ons.ui import UI
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Create a "progress bar" using UI elements.
"""

c = Controller()
c.communicate({"$type": "set_target_framerate",
               "framerate": 30})
camera = ThirdPersonCamera(position={"x": -3.75, "y": 1.5, "z": -0.5},
                           look_at={"x": 0, "y": 0, "z": 0},
                           avatar_id="a")
ui = UI()
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("progress_bar")
print(f"Images will be saved to: {path}")
capture = ImageCapture(path=path, avatar_ids=["a"])
c.add_ons.extend([camera, capture, ui])
c.communicate(Controller.get_add_scene(scene_name="tdw_room"))
ui.attach_canvas_to_avatar(avatar_id="a")
# Get the image.
image = "white.png"
# Set the dimensions of the progress bar.
progress_bar_position = {"x": 16, "y": -16}
progress_bar_size = {"x": 16, "y": 16}
progress_bar_scale = {"x": 10, "y": 2}
progress_bar_anchor = {"x": 0, "y": 1}
progress_bar_pivot = {"x": 0, "y": 1}
# Add the background sprite.
ui.add_image(image=image,
             position=progress_bar_position,
             size=progress_bar_size,
             anchor=progress_bar_anchor,
             pivot=progress_bar_pivot,
             color={"r": 0, "g": 0, "b": 0, "a": 1},
             scale_factor=progress_bar_scale,
             rgba=False)
# Add the foreground sprite.
progress_width = 0
bar_id = ui.add_image(image=image,
                      position=progress_bar_position,
                      size=progress_bar_size,
                      anchor=progress_bar_anchor,
                      pivot=progress_bar_pivot,
                      color={"r": 1, "g": 0, "b": 0, "a": 1},
                      scale_factor={"x": 0, "y": progress_bar_scale["y"]},
                      rgba=False)
# Add some text.
text_id = ui.add_text(text="Progress: 0%",
                      position=progress_bar_position,
                      anchor=progress_bar_anchor,
                      pivot=progress_bar_pivot,
                      font_size=18)
# Initialize the UI.
c.communicate([])
progress = 0
for i in range(100):
    progress += 1
    progress_width += 0.01
    # Update the text.
    ui.set_text(ui_id=text_id,
                text=f"Progress: {progress}%",)
    # Update the bar.
    ui.set_size(ui_id=bar_id,
                size={"x": int(progress_bar_size["x"] * progress_bar_scale["x"] * progress_width),
                      "y": int(progress_bar_size["y"] * progress_bar_scale["y"])})
    # Advance one frame.
    c.communicate([])
c.communicate({"$type": "terminate"})
