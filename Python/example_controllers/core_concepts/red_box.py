from time import sleep
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera

"""
Add a box and make it red.
"""

c = Controller()

# Generate a unique object ID.
object_id = c.get_unique_id()
# Add a camera and look at the object (we haven't added the object yet but this will execute after adding the object).
cam = ThirdPersonCamera(position={"x": 2, "y": 1.6, "z": -0.6},
                        look_at=object_id)
c.add_ons.append(cam)
# Create the scene, add the object, and make the object red.
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="iron_box",
                                library="models_core.json",
                                position={"x": 1, "y": 0, "z": -0.5},
                                object_id=object_id),
               {"$type": "set_color",
                "color": {"r": 1.0, "g": 0, "b": 0, "a": 1.0},
                "id": object_id}])
sleep(2)
c.communicate({"$type": "terminate"})
