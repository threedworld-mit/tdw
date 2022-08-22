# 961
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.benchmark import Benchmark
from tdw.add_ons.obi import Obi
from tdw.obi_data.cloth.sheet_type import SheetType

"""
Benchmark an Obi cloth simulation.
"""

c = Controller(launch_build=False)
benchmark = Benchmark()
for output_data in [True, False]:
    c.add_ons.clear()
    obi = Obi(output_data=output_data)
    c.add_ons.extend([obi, benchmark])
    cloth_id = Controller.get_unique_id()
    obi.create_cloth_sheet(object_id=cloth_id,
                           position={"x": 0, "y": 2, "z": 0},
                           cloth_material="cotton",
                           sheet_type=SheetType.cloth_vhd)
    c.communicate([{"$type": "load_scene",
                    "scene_name": "ProcGenScene"},
                   TDWUtils.create_empty_room(12, 12)])
    benchmark.start()
    for i in range(1000):
        c.communicate([])
        if i == 0 and output_data:
            print(f"Particle count: {len(obi.actors[cloth_id].positions)}")
    benchmark.stop()
    print("Output data:", output_data, "FPS:", benchmark.fps)
c.communicate({"$type": "terminate"})
