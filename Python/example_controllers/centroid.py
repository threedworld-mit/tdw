from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import ModelLibrarian

# Get the model name and the model record.
model_name = "vase_02"
lib = ModelLibrarian()
record = lib.get_record(model_name)
y = 2
c = Controller(launch_build=False)
# Add a camera. Set the y (height) of the camera to the object centroid height.
camera = ThirdPersonCamera(avatar_id="a",
                           position={"x": 0, "y": y + record.bounds["center"]["y"], "z": -1})
c.add_ons.append(camera)
# Create the scene and add the object.
object_id = Controller.get_unique_id()
commands = [TDWUtils.create_empty_room(12, 12),
            {"$type": "set_target_framerate",
             "framerate": 30}]
commands.extend(Controller.get_add_physics_object(model_name="rh10",
                                                  object_id=object_id,
                                                  position={"x": 0, "y": y, "z": 0},
                                                  kinematic=True))
c.communicate(commands)
delta = 15
for axis in ["pitch", "yaw", "roll"]:
    angle = 0
    while angle < 360:
        c.communicate({"$type": "rotate_object_by",
                       "angle": delta,
                       "id": object_id,
                       "axis": axis,
                       "use_centroid": True})
        angle += delta
c.communicate({"$type": "terminate"})
