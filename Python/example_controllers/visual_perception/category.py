from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, SegmentationColors, Categories
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Get the _category pass and category data per object.
"""

c = Controller()
object_id_0 = c.get_unique_id()
object_id_1 = c.get_unique_id()
object_id_2 = c.get_unique_id()
object_id_3 = c.get_unique_id()
object_names = {object_id_0: "small_table_green_marble",
                object_id_1: "rh10",
                object_id_2: "jug01",
                object_id_3: "jug05"}

output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("category")

# Enable image capture for the _category pass.
print(f"Images will be saved to: {output_directory}")
capture = ImageCapture(path=output_directory, pass_masks=["_category"], avatar_ids=["a"])
c.add_ons.append(capture)

commands = [TDWUtils.create_empty_room(12, 12),
            c.get_add_object(object_names[object_id_0],
                             object_id=object_id_0),
            c.get_add_object(object_names[object_id_1],
                             position={"x": 0.7, "y": 0, "z": 0.4},
                             rotation={"x": 0, "y": 30, "z": 0},
                             object_id=object_id_1),
            c.get_add_object(model_name=object_names[object_id_2],
                             position={"x": -0.3, "y": 0.9, "z": 0.2},
                             object_id=object_id_2),
            c.get_add_object(object_names[object_id_3],
                             position={"x": 0.3, "y": 0.9, "z": -0.2},
                             object_id=object_id_3),
            {"$type": "send_categories",
             "frequency": "once"},
            {"$type": "send_segmentation_colors",
             "frequency": "once"}]

commands.extend(TDWUtils.create_avatar(position={"x": 2.478, "y": 1.602, "z": 1.412},
                                       look_at={"x": 0, "y": 0.2, "z": 0},
                                       avatar_id="a"))
resp = c.communicate(commands)
# Get each object category and category color.
object_categories = dict()
category_colors = dict()
for i in range(len(resp) - 1):
    r_id = OutputData.get_data_type_id(resp[i])
    if r_id == "segm":
        segm = SegmentationColors(resp[i])
        for j in range(segm.get_num()):
            object_id = segm.get_object_id(j)
            object_category = segm.get_object_category(j)
            object_categories[object_id] = object_category
    elif r_id == "cate":
        cate = Categories(resp[i])
        for j in range(cate.get_num_categories()):
            category_name = cate.get_category_name(j)
            category_color = cate.get_category_color(j)
            category_colors[category_name] = category_color
# Print the category colors of each object.
for object_id in object_categories:
    category_name = object_categories[object_id]
    object_category_color = category_colors[category_name]
    print(object_id, category_name, object_category_color)
c.communicate({"$type": "terminate"})
