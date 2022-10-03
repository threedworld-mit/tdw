from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, SegmentationColors, IdPassSegmentationColors

"""
Get the IDs of each object in the frame.
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
commands.extend([{"$type": "set_pass_masks",
                  "avatar_id": "a",
                  "pass_masks": ["_id"]},
                 {"$type": "send_segmentation_colors",
                  "frequency": "once"},
                 {"$type": "send_id_pass_segmentation_colors",
                  "frequency": "always"}])
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
    for i in range(len(segmentation_colors_in_image)):
        if any((segmentation_colors_in_image[i] == j).all() for j in segmentation_colors_per_object.values()):
            print(object_id)
            break
c.communicate({"$type": "terminate"})
