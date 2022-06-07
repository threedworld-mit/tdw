from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.mouse import Mouse
from tdw.add_ons.third_person_camera import ThirdPersonCamera

"""
Click on objects to print their IDs.
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
camera = ThirdPersonCamera(position={"x": 2.478, "y": 1.602, "z": 1.412},
                           look_at={"x": 0, "y": 0.2, "z": 0},
                           avatar_id="a")
mouse = Mouse(avatar_id="a")
c.add_ons.extend([camera, mouse])
c.communicate([TDWUtils.create_empty_room(12, 12),
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
                                object_id=object_id_3)])
done = False
while not done:
    # End the simulation.
    if mouse.right_button_pressed:
        done = True
    # We clicked on an object.
    elif mouse.left_button_pressed and mouse.mouse_is_over_object:
        print(mouse.mouse_over_object_id)
    c.communicate([])
c.communicate({"$type": "terminate"})
