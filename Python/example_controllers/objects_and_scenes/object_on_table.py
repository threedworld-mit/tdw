from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Bounds
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Use Bounds data to put an object on a table.
"""

c = Controller()
object_id = c.get_unique_id()

# Add a camera and enable image capture.
cam = ThirdPersonCamera(position={"x": 2.478, "y": 1.602, "z": 1.412},
                        look_at={"x": 0, "y": 0.5, "z": 0},)
output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("bounds")
print(f"Images will be saved to: {output_directory.resolve()}")
c.add_ons.append(cam)
cap = ImageCapture(path=output_directory, avatar_ids=[cam.avatar_id], pass_masks=["_img"])
c.add_ons.append(cap)
# Create the scene. Add a table. Request Bounds output data.
resp = c.communicate([TDWUtils.create_empty_room(12, 12),
                      c.get_add_object(model_name="small_table_green_marble",
                                       position={"x": 0, "y": 0, "z": 0},
                                       object_id=object_id),
                      {"$type": "send_bounds",
                       "frequency": "once"}])

# Get the top of the table.
top = (0, 0, 0)
for i in range(len(resp) - 1):
    r_id = OutputData.get_data_type_id(resp[i])
    if r_id == "boun":
        bounds = Bounds(resp[i])
        for j in range(bounds.get_num()):
            if bounds.get_id(j) == object_id:
                top = bounds.get_top(j)
                break
# Put an object on top of the table.
c.communicate(c.get_add_object(model_name="jug01",
                               position=TDWUtils.array_to_vector3(top),
                               object_id=c.get_unique_id()))
c.communicate({"$type": "terminate"})