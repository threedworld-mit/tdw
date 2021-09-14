from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera


"""
Follow the position of an object.
"""

c = Controller()

object_id = c.get_unique_id()
# Create a third-person camera that will follow the object.
cam = ThirdPersonCamera(avatar_id="a",
                        position={"x": 2, "y": 1.6, "z": -0.6},
                        follow_object=object_id,
                        follow_rotate=False,
                        look_at=object_id)
c.add_ons.append(cam)
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="iron_box",
                                library="models_core.json",
                                position={"x": 1, "y": 0, "z": -0.5},
                                object_id=object_id),
               {"$type": "apply_force_to_object",
                "id": object_id,
                "force": {"x": -15, "y": 2, "z": 3}}])
for i in range(100):
    c.communicate([])
# Stop following the object.
cam.follow_object = None
c.communicate({"$type": "terminate"})