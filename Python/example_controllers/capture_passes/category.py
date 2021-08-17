from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, SegmentationColors, IdPassSegmentationColors
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.librarian import ModelLibrarian

"""
Get the IDs of each object in the frame.
"""

c = Controller()
c.start()
object_id_0 = c.get_unique_id()
object_id_1 = c.get_unique_id()
object_id_2 = c.get_unique_id()
object_id_3 = c.get_unique_id()
object_names = {object_id_0: "small_table_green_marble",
                object_id_1: "rh10",
                object_id_2: "jug01",
                object_id_3: "jug05"}

# Get the category of each object.
object_categories = dict()
lib = ModelLibrarian()
for object_id in object_names:
    record = lib.get_record(object_names[object_id])
    object_categories[object_id] = record.wcategory

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
                             object_id=object_id_3)]

commands.extend(TDWUtils.create_avatar(position={"x": 2.478, "y": 1.602, "z": 1.412},
                                       look_at={"x": 0, "y": 0.2, "z": 0},
                                       avatar_id="a"))
commands.append({"$type": "send_categories",
                 "frequency": "once"})
resp = c.communicate(commands)
# Get each segmentation color.
segmentation_colors_per_object = dict()
segmentation_colors_in_image = list()
for i in range(len(resp) - 1):
    r_id = OutputData.get_data_type_id(resp[i])
    # Get segmentation color output data.
    if r_id == "segm":
        segm = SegmentationColors(resp[i])
        for j in range(segm.get_num()):
            object_id = segm.get_object_id(j)
            object_name = object_names[object_id]
            segmentation_color = segm.get_object_color(j)
            segmentation_colors_per_object[object_id] = segmentation_color
    elif r_id == "ipsc":
        ipsc = IdPassSegmentationColors(resp[i])
        for j in range(ipsc.get_num_segmentation_colors()):
            segmentation_colors_in_image.append(ipsc.get_segmentation_color(j))
# Print the ID of each object in the image.
for object_id in segmentation_colors_per_object:
    if segmentation_colors_per_object[object_id] in segmentation_colors_in_image:
        print(object_id)
c.communicate({"$type": "terminate"})
