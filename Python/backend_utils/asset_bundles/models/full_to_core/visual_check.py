from pathlib import Path
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

"""
Verify that the records of each new model are ok.
"""

c = Controller(launch_build=False)
print("Launch the build in Unity Editor.")
commands = [TDWUtils.create_empty_room(12, 12)]
models = Path("full_to_core.txt").read_text().strip().split("\n")
y = 0
for m in models:
    commands.append(c.get_add_object(model_name=m,
                                     object_id=c.get_unique_id(),
                                     position={"x": 0, "y": y, "z": 0},
                                     library="models_full.json"))
    y += 1.5
c.communicate(commands)
