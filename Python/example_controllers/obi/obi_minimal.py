from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.obi import Obi

"""
A minimal implementation of Obi.
"""

c = Controller()
# Create the Obi add-on.
obi = Obi()
c.add_ons.append(obi)
# Create a scene and add the object.
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(Controller.get_add_physics_object(model_name="rh10",
                                                  object_id=Controller.get_unique_id()))
# Send the commands and initialize Obi.
c.communicate(commands)
c.communicate([])
