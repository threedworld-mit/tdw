from pathlib import Path
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import ModelLibrarian
from tdw.output_data import OutputData, Bounds, Images

lib = ModelLibrarian("models_core.json")
# Get the record for the table.
table_record = lib.get_record("small_table_green_marble")

c = Controller()

table_id = 0

# 1. Load the scene.
# 2. Create an empty room (using a wrapper function)
# 3. Add the table.
# 4. Request Bounds data.
resp = c.communicate([{"$type": "load_scene",
                       "scene_name": "ProcGenScene"},
                      TDWUtils.create_empty_room(12, 12),
                      c.get_add_object(model_name=table_record.name,
                                       object_id=table_id,
                                       position={"x": 0, "y": 0, "z": 0},
                                       rotation={"x": 0, "y": 0, "z": 0}),
                      {"$type": "send_bounds",
                       "ids": [table_id],
                       "frequency": "once"}])

# Get the top of the table.
top_y = 0
for r in resp[:-1]:
    r_id = OutputData.get_data_type_id(r)
    # Find the bounds data.
    if r_id == "boun":
        b = Bounds(r)
        # We only requested the table, so it is object 0:
        _, top_y, _ = b.get_top(0)

box_record = lib.get_record("puzzle_box_composite")
box_id = 1
c.communicate(c.get_add_object(model_name=box_record.name,
                               object_id=box_id,
                               position={"x": 0, "y": top_y, "z": 0},
                               rotation={"x": 0, "y": 0, "z": 0}))

avatar_id = "a"
resp = c.communicate([{"$type": "create_avatar",
                       "type": "A_Img_Caps_Kinematic",
                       "avatar_id": avatar_id},
                      {"$type": "teleport_avatar_to",
                       "position": {"x": 1, "y": 2.5, "z": 2},
                       "avatar_id": avatar_id},
                      {"$type": "look_at",
                       "avatar_id": avatar_id,
                       "object_id": box_id},
                      {"$type": "set_pass_masks",
                       "avatar_id": avatar_id,
                       "pass_masks": ["_img"]},
                      {"$type": "send_images",
                       "frequency": "once",
                       "avatar_id": avatar_id}])

# Get the image.
for r in resp[:-1]:
    r_id = OutputData.get_data_type_id(r)
    # Find the image data.
    if r_id == "imag":
        img = Images(r)

        # Usually, you'll want to use one of these functions, but not both of them:

        # Use this to save a .jpg
        TDWUtils.save_images(img, filename="test_img")

        print(f"Image saved to: {Path('dist/test_img.jpg').resolve()}")

        # Use this to convert the image to a PIL image, which can be processed by a ML system at runtime.
        # The index is 0 because we know that there is only one pass ("_img").
        pil_img = TDWUtils.get_pil_image(img, index=0)
