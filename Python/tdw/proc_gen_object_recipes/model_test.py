import json
from pathlib import Path
import numpy as np
from tdw.librarian import ModelLibrarian
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

path = Path("models.json")
data = json.loads(path.read_text(encoding="utf-8"))
print("\n".join(data.keys()))
exit()
wnid = "n02933112"
lib = ModelLibrarian("models_full.json")
wnids = lib.get_model_wnids_and_wcategories()
wcategory = ""
pcategory = "cabinet"
for q in wnids:
    print(q, wnids[q])
    if q == wnid:
        wcategory = wnids[q]
records = lib.get_all_models_in_wnid(wnid)
names = []
x = -4
xs = []
exclude = ["kitchen_sieve", "b03_orange_(3dsmax2013_vray2)", "b05_06_oranges_in_a_bowl"]
for record in records:
    if not record.do_not_use and record.name not in exclude:
        b = TDWUtils.bytes_to_megabytes(record.asset_bundle_sizes["Windows"])
        r = TDWUtils.vector3_to_array(record.canonical_rotation)
        if b < 50 and np.linalg.norm(r) == 0:
            print(record.name, b)
            names.append(record.name)
            width = np.linalg.norm(
                TDWUtils.vector3_to_array(record.bounds["left"]) - TDWUtils.vector3_to_array(record.bounds["right"]))
            xs.append(x)
            x += width
path = Path("models.json")
data = json.loads(path.read_text(encoding="utf-8"))
if len(names) == 0:
    if pcategory in data:
        del data[pcategory]
        path.write_text(json.dumps(data, indent=2, sort_keys=True))
else:
    data[pcategory] = names
    path.write_text(json.dumps(data, indent=2, sort_keys=True))
path = Path("procgen_category_to_wcategory.json")
data = json.loads(path.read_text(encoding="utf-8"))
if len(names) == 0:
    if pcategory in data:
        del data[pcategory]
        path.write_text(json.dumps(data, indent=2, sort_keys=True))
else:
    data[pcategory] = wcategory
    path.write_text(json.dumps(data, indent=2, sort_keys=True))
if len(names) == 0:
    exit()
#exit()
commands = [TDWUtils.create_empty_room(12, 12)]
for name, ix in zip(names, xs):
    commands.append(Controller.get_add_object(model_name=name,
                                              position={"x": ix, "y": 0, "z": 0},
                                              object_id=Controller.get_unique_id(),
                                              library="models_full.json"))
c = Controller(launch_build=False)
c.communicate(commands)
