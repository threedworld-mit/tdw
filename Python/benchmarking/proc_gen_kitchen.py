from pathlib import Path
from json import loads
from tdw.controller import Controller
from tdw.add_ons.container_manager import ContainerManager
from tdw.add_ons.object_manager import ObjectManager
from tdw.add_ons.composite_object_manager import CompositeObjectManager
from tdw.add_ons.benchmark import Benchmark

"""
Benchmark the output data of object data (`Transforms`, `DynamicCompositeObjects`, and `Overlap`) in a kitchen scene created by `ProcGenKitchen`.
Note that `ProcGenKitchen` isn't actually used; in order to reliably re-create the scene, this benchmark uses cached commands.
"""

c = Controller()
# Load the scene.
c.communicate(loads(Path("kitchen_commands.json").read_text()))
benchmark = Benchmark()
# Initialize the add-ons.
object_manager = ObjectManager(transforms=True, rigidbodies=False, bounds=False)
c.add_ons.extend([object_manager,
                  ContainerManager(),
                  CompositeObjectManager(),
                  benchmark])
c.communicate([])
benchmark.start()
for i in range(2000):
    c.communicate([])
benchmark.stop()
print(benchmark.fps)
c.communicate({"$type": "terminate"})
