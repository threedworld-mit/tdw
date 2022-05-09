from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.container_manager import ContainerManager
from tdw.add_ons.benchmark import Benchmark

"""
Benchmark containment data.
"""

c = Controller()
container_manager = ContainerManager()
benchmark = Benchmark()
c.add_ons = [container_manager, benchmark]
room_size = 20
d = room_size // 2 - 2
commands = [TDWUtils.create_empty_room(room_size, room_size)]
for x in range(-d, d):
    for z in range(-d, d):
        commands.extend(Controller.get_add_physics_object(model_name="int_kitchen_accessories_le_creuset_bowl_30cm",
                                                          object_id=Controller.get_unique_id(),
                                                          position={"x": x, "y": 0, "z": z},
                                                          library="models_core.json"))
        commands.extend(Controller.get_add_physics_object(model_name="octahedron",
                                                          object_id=Controller.get_unique_id(),
                                                          position={"x": x, "y": 2, "z": z},
                                                          rotation={"x": 1, "y": 0, "z": 0},
                                                          library="models_flex.json",
                                                          default_physics_values=False,
                                                          bounciness=0.9,
                                                          dynamic_friction=0.1,
                                                          static_friction=0.1,
                                                          mass=1,
                                                          scale_mass=False,
                                                          scale_factor={"x": 0.1, "y": 0.1, "z": 0.1}))
c.communicate(commands)
benchmark.start()
for i in range(2000):
    c.communicate([])
benchmark.stop()
print(benchmark.fps)
c.communicate({"$type": "terminate"})
