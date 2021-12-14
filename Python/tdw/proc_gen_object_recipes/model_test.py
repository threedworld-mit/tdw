import json
from pathlib import Path
import numpy as np
from tdw.librarian import ModelLibrarian
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils


"""
cabinet
vase
kitchen utensil
cup
candle
orange
jug
jar
plate
carving fork
shelf
sink
"""

wnid = "n02948072"
lib = ModelLibrarian("models_full.json")
wnids = lib.get_model_wnids_and_wcategories()
category = "candle"
for q in wnids:
    print(q, wnids[q])
records = lib.get_all_models_in_wnid(wnid)
sizes = dict()
x = -4
xs = []
exclude = ["b03_pot_plant_20_2013__vray", "b04_cgaxis_models_50_06_vray", "ficus", "pot_plant_23_2013__vray", "monstera_plant", "philodendron"]
for record in records:
    if not record.do_not_use and record.name not in exclude:
        b = TDWUtils.bytes_to_megabytes(record.asset_bundle_sizes["Windows"])
        r = TDWUtils.vector3_to_array(record.canonical_rotation)
        if b < 100 and np.linalg.norm(r) == 0:
            print(record.name, b)
            width = np.linalg.norm(
                TDWUtils.vector3_to_array(record.bounds["left"]) - TDWUtils.vector3_to_array(record.bounds["right"]))
            height = np.linalg.norm(
                TDWUtils.vector3_to_array(record.bounds["top"]) - TDWUtils.vector3_to_array(record.bounds["bottom"]))
            length = np.linalg.norm(
                TDWUtils.vector3_to_array(record.bounds["front"]) - TDWUtils.vector3_to_array(record.bounds["back"]))
            sizes[record.name] = [round(width, 8), round(height, 8), round(length, 8)]
            xs.append(x)
            x += width
path = Path.home().joinpath("tdw/Python/tdw/proc_gen_object_recipes/models.json")
data = json.loads(path.read_text(encoding="utf-8"))
if len(sizes) == 0:
    if category in data:
        del data[category]
        path.write_text(json.dumps(data, indent=2, sort_keys=True))
    exit()
else:
    data[category] = sizes
path.write_text(json.dumps(data, indent=2, sort_keys=True))
#exit()
commands = [TDWUtils.create_empty_room(12, 12)]
for name, ix in zip(sizes, xs):
    commands.append(Controller.get_add_object(model_name=name,
                                              position={"x": ix, "y": 0, "z": 0},
                                              object_id=Controller.get_unique_id(),
                                              library="models_full.json"))
c = Controller(launch_build=False)
c.communicate(commands)
