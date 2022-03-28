from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.benchmark import Benchmark
from tdw.add_ons.obi import Obi
from tdw.obi_data.fluids.cube_emitter import CubeEmitter

"""
Benchmark an Obi fluid simulation.
"""

c = Controller(launch_build=False)
benchmark = Benchmark()
for output_data in [True, False]:
    camera = ThirdPersonCamera(position={"x": 1.2, "y": 1.5, "z": -1.5},
                               look_at={"x": 0, "y": 0, "z": 0})
    c.add_ons.clear()
    obi = Obi(output_data=output_data)
    c.add_ons.extend([camera, obi, benchmark])
    obi.create_fluid(fluid="honey",
                     shape=CubeEmitter(size={"x": 1, "y": 1, "z": 1}),
                     object_id=Controller.get_unique_id(),
                     position={"x": 0, "y": 2.35, "z": 0},
                     rotation={"x": 90, "y": 0, "z": 0},
                     speed=1)
    c.communicate(TDWUtils.create_empty_room(12, 12))
    benchmark.start()
    for i in range(1000):
        c.communicate([])
    benchmark.stop()
    print("Output data:", output_data, "FPS:", benchmark.fps)
c.communicate({"$type": "terminate"})
