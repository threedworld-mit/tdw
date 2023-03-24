from tdw.controller import Controller
from tdw.add_ons.image_capture import ImageCapture
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.floorplan_flood import FloorplanFlood
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


"""
Generate a floorplan scene and populate it with a layout of objects.
"""

c = Controller(launch_build=False)

# Initialize the floorplan add-on.
floorplan_flood = FloorplanFlood()
# Scene 1, visual variant a, object layout 0.
floorplan_flood.init_scene(scene="1a", layout=0)

# Add a camera and enable image capture.
camera = ThirdPersonCamera(position={"x": 0, "y": 40, "z": 0},
                           look_at={"x": 0, "y": 0, "z": 0},
                           avatar_id="a")
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("floorplan_controller")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"], pass_masks=["_img"], path=path)

c.add_ons.extend([floorplan_flood, camera, capture])
# Initialize the scene.
c.communicate([])
# Make the image 720p and hide the roof.
c.communicate([{"$type": "set_screen_size",
                "width": 1280,
                "height": 720},
               {"$type": "set_floorplan_roof",
                "show": False}])
# Flood the floor section #1
floorplan_flood.add_flood_section(1)
floorplan_flood.add_flood_section(2)
floorplan_flood.add_flood_section(3)
for i in range(50):
    floorplan_flood.set_flood_height(1, 0.01)
for j in range(40):
    floorplan_flood.set_flood_height(2, 0.01)
for k in range(30):
    floorplan_flood.set_flood_height(3, 0.01)
#c.communicate({"$type": "terminate"})
