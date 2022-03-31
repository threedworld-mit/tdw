from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.benchmark import Benchmark
from tdw.flex_data.fluid_type import FLUID_TYPES

"""
Benchmark a Flex fluid simulation.
"""

c = Controller(launch_build=False)
camera = ThirdPersonCamera(position={"x": 1.2, "y": 1.5, "z": -1.5},
                           look_at={"x": 0, "y": 0, "z": 0})
fluid_name = "honey"
fluid = FLUID_TYPES[fluid_name]
fluid_id = Controller.get_unique_id()
benchmark = Benchmark()
c.add_ons.extend([camera, benchmark])
c.communicate([TDWUtils.create_empty_room(12, 12),
               {'$type': 'convexify_proc_gen_room'},
               {"$type": "create_flex_container",
                "collision_distance": 0.04,
                "static_friction": 0.1,
                "dynamic_friction": 0.1,
                "particle_friction": 0.1,
                "viscocity": fluid.viscosity,
                "adhesion": fluid.adhesion,
                "cohesion": fluid.cohesion,
                "radius": 0.1,
                "fluid_rest": 0.05,
                "damping": 0.01,
                "substep_count": 5,
                "iteration_count": 8,
                "buoyancy": 1.0},
               {"$type": "load_flex_fluid_from_resources",
                "id": fluid_id,
                "orientation": {"x": 0, "y": 0, "z": 0},
                "position": {"x": 0, "y": 2.35, "z": 0}},
               {"$type": "set_flex_fluid_actor",
                "id": fluid_id,
                "mass_scale": 1.0,
                "particle_spacing": 0.05},
               {"$type": "assign_flex_container",
                "id": fluid_id,
                "container_id": 0,
                "fluid_container": True,
                "fluid_type": fluid_name}])
benchmark.start()
for i in range(1000):
    c.communicate([])
benchmark.stop()
print(benchmark.fps)
c.communicate({"$type": "terminate"})
