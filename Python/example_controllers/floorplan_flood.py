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
camera = ThirdPersonCamera(position={"x":-5, "y": 6.4, "z": -2.6},
                           look_at={"x": -2.25, "y": 0.05, "z": 2.5},
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
               {"$type": "set_field_of_view", "field_of_view": 82, "avatar_id": "a"},
               {"$type": "set_floorplan_roof",
                "show": False}])
flood_start_floor = 4
for i in range(50):
    floorplan_flood.set_flood_height(flood_start_floor, 0.0125)
    c.communicate([])
adjacent_floors = floorplan_flood.get_adjacent_floors(flood_start_floor)
for f in adjacent_floors:
    for i in range(50):
        floorplan_flood.set_flood_height(f, 0.0125)
        c.communicate([])
bowl_id = self.get_unique_id()
chair_id = self.get_unique_id()
c.communicate([c.get_add_object(model_name="elephant_bowl",
                                              object_id=bowl_id
                                              position={"x": -2.8, "y": 0, "z": 2.5},
                                              rotation={"x": 0, "y": 0, "z": 0}),
               c.get_add_object(model_name="chair_thonet_marshall",
                                              object_id=chair_id,
                                              position={"x": -2.0, "y": 0, "z": 2.0},
                                              rotation={"x": 0, "y": 0, "z": 0}),
              {"$type": "add_floorplan_flood_buoyancy", "id": bowl_id},
              {"$type": "add_floorplan_flood_buoyancy", "id": chair_id}])


#c.communicate({"$type": "terminate"})
