from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.first_person_avatar import FirstPersonAvatar

"""
A minimal example of a first-person avatar.
"""

c = Controller()
a = FirstPersonAvatar()
c.add_ons.append(a)
c.communicate([TDWUtils.create_empty_room(12, 12),
               Controller.get_add_object(model_name="rh10",
                                         position={"x": 2, "y": 0, "z": 2},
                                         object_id=Controller.get_unique_id())])
done = False
while not done:
    c.communicate([])
    if a.mouse_is_over_object and a.left_button_pressed:
        print(a.mouse_over_object_id)
    if a.right_button_pressed:
        done = True
c.communicate({"$type": "terminate"})
