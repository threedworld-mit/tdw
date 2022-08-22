from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.benchmark import Benchmark
from tdw.output_data import FlexParticles

"""
Benchmark a Flex cloth simulation.
"""

c = Controller(launch_build=False)
benchmark = Benchmark()
c.add_ons.append(benchmark)
for output_data in [True, False]:
    cloth_id = c.get_unique_id()
    commands = [{"$type": "load_scene",
                 "scene_name": "ProcGenScene"},
                TDWUtils.create_empty_room(12, 12),
                {'$type': 'convexify_proc_gen_room'},
                {'$type': 'create_flex_container'},
                c.get_add_object(model_name="cloth_square",
                                 object_id=cloth_id,
                                 library="models_special.json",
                                 position={"x": 0, "y": 2, "z": 0}),
                {"$type": "set_flex_cloth_actor",
                 "id": cloth_id,
                 "mass_scale": 1,
                 "mesh_tesselation": 1,
                 "tether_stiffness": 0.5,
                 "bend_stiffness": 1.0,
                 "self_collide": False,
                 "stretch_stiffness": 1.0},
                {"$type": "assign_flex_container",
                 "id": cloth_id,
                 "container_id": 0}]
    if output_data:
        commands.append({"$type": "send_flex_particles",
                         "frequency": "always"})
    resp = c.communicate(commands)
    benchmark.start()
    if output_data:
        print(f"Particle count: {len(FlexParticles(resp[0]).get_particles(0))}")
    for i in range(1000):
        c.communicate([])
    benchmark.stop()
    print("Output data:", output_data, "FPS:", benchmark.fps)
c.communicate({"$type": "terminate"})
