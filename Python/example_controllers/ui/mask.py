from io import BytesIO
from PIL import Image, ImageDraw
from tdw.controller import Controller
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.ui import UI
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


"""
Create black background with a circular "hole" in it and move the image around.
"""


c = Controller()
# Add the UI add-on and the camera.
camera = ThirdPersonCamera(position={"x": 0, "y": 0, "z": -1.2},
                           avatar_id="a")
ui = UI()
c.add_ons.extend([camera, ui])
ui.attach_canvas_to_avatar(avatar_id="a")
screen_size = 512
commands = [{"$type": "create_empty_environment"},
            {"$type": "set_screen_size",
             "width": screen_size,
             "height": screen_size}]
# Add a cube slightly off-center.
commands.extend(Controller.get_add_physics_object(model_name="cube",
                                                  library="models_flex.json",
                                                  object_id=0,
                                                  position={"x": 0.25, "y": 0, "z": 1},
                                                  rotation={"x": 30, "y": 10, "z": 0},
                                                  kinematic=True))
c.communicate(commands)

# Enable image capture.
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("ui_mask")
print(f"Images will be saved to: {path}")
capture = ImageCapture(path=path, avatar_ids=["a"])
c.add_ons.append(capture)

# Create the UI image with PIL.
# The image is larger than the screen size so we can move it around.
image_size = screen_size * 3
image = Image.new(mode="RGBA", size=(image_size, image_size), color=(0, 0, 0, 255))
# Draw a circle on the mask.
draw = ImageDraw.Draw(image)
diameter = 256
d = image_size // 2 - diameter // 2
draw.ellipse([(d, d), (d + diameter, d + diameter)], fill=(0, 0, 0, 0))
# Convert the PIL image to bytes.
with BytesIO() as output:
    image.save(output, "PNG")
    mask = output.getvalue()
x = 0
y = 0
# Add the image.
mask_id = ui.add_image(image=mask, position={"x": x, "y": y}, size={"x": image_size, "y": image_size}, raycast_target=False)
c.communicate([])

# Move the image.
for i in range(100):
    x += 4
    y += 3
    ui.set_position(ui_id=mask_id, position={"x": x, "y": y})
    c.communicate([])
c.communicate({"$type": "terminate"})
