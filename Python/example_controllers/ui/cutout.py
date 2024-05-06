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

# Create the background UI image.
bg_size = screen_size * 2
base_id = ui.add_image(image=Image.new(mode="RGBA", size=(bg_size, bg_size), color=(0, 0, 0, 255)),
                       position={"x": 0, "y": 0},
                       size={"x": bg_size, "y": bg_size})

# Create the cutout image.
diameter = 256
mask = Image.new(mode="RGBA", size=(diameter, diameter), color=(0, 0, 0, 0))
# Draw a circle.
draw = ImageDraw.Draw(mask)
draw.ellipse([(0, 0), (diameter, diameter)], fill=(255, 255, 255, 255))
x = 0
y = 0
# Add the cutout.
cutout_id = ui.add_cutout(image=mask, position={"x": x, "y": y}, size={"x": diameter, "y": diameter}, base_id=base_id)
c.communicate([])

# Move the cutout.
for i in range(100):
    x += 4
    y += 3
    ui.set_position(ui_id=cutout_id, position={"x": x, "y": y})
    c.communicate([])
c.communicate({"$type": "terminate"})
