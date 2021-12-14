import json
from pathlib import Path
import numpy as np
from tdw.librarian import ModelLibrarian
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils


"""
cabinet
croissant
donut
soda can
tea tray
vase
pepper mill, pepper grinder
apple
kitchen utensil
banana
patty, cake
beverage
chocolate candy
cup
candle
teakettle
orange
pen
jug
houseplant
jar
grape
bowl
saltshaker, salt shaker
bottle cork
coffee maker
Coffee pot
coffee
plate
coaster
carving fork
raw vegetable
sandwich
pizza
table
chair
bottle
shelf
ipod
coin
scissors
sink
book
pencil
"""

wnid = "n03063338"
lib = ModelLibrarian("models_full.json")
wnids = lib.get_model_wnids_and_wcategories()
category = "coffee_maker"
for q in wnids:
    print(q, wnids[q])
records = lib.get_all_models_in_wnid(wnid)
sizes = dict()
x = -4
xs = []
for record in records:
    if not record.do_not_use:
        b = TDWUtils.bytes_to_megabytes(record.asset_bundle_sizes["Windows"])
        r = TDWUtils.vector3_to_array(record.canonical_rotation)
        if b < 20 and np.linalg.norm(r) == 0:
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
data[category] = sizes
path.write_text(json.dumps(data, indent=2, sort_keys=True))
exit()
commands = [TDWUtils.create_empty_room(12, 12)]
for name, ix in zip(sizes, xs):
    commands.append(Controller.get_add_object(model_name=name,
                                              position={"x": ix, "y": 0, "z": 0},
                                              object_id=Controller.get_unique_id(),
                                              library="models_full.json"))
c = Controller(launch_build=False)
c.communicate(commands)
