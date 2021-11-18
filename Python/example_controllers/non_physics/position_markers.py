from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Bounds
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Visualize the bounds of an object with position markers.
"""

c = Controller()
camera = ThirdPersonCamera(avatar_id="a",
                           position={"x": 3.83, "y": 6, "z": -0.71},
                           look_at={"x": 0, "y": 0, "z": 0})
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("position_markers")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"], path=path)
c.add_ons.extend([camera, capture])
object_id = c.get_unique_id()
# Create the scene. Add the object. Request bounds data.
resp = c.communicate([TDWUtils.create_empty_room(12, 12),
                      c.get_add_object(model_name="arflex_hollywood_sofa",
                                       object_id=object_id,
                                       position={"x": 1, "y": 0, "z": 0},
                                       rotation={"x": 0, "y": 31, "z": 0}),
                      {"$type": "send_bounds",
                       "frequency": "once"}])
commands = []
for i in range(len(resp) - 1):
    r_id = OutputData.get_data_type_id(resp[i])
    if r_id == "boun":
        bounds = Bounds(resp[i])
        for j in range(bounds.get_num()):
            if bounds.get_id(j) == object_id:
                for bound_position in [bounds.get_top(j), bounds.get_bottom(j), bounds.get_left(j), bounds.get_right(j),
                                       bounds.get_front(j), bounds.get_bottom(j)]:
                    commands.append({"$type": "add_position_marker",
                                     "position": TDWUtils.array_to_vector3(bound_position),
                                     "scale": 0.2})
c.communicate(commands)
c.communicate({"$type": "terminate"})
