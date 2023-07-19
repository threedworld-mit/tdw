from tdw.controller import Controller
from tdw.add_ons.obi import Obi
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.obi_data.fluids.cube_emitter import CubeEmitter
from tdw.obi_data.fluids.fluid import Fluid
from tdw.tdw_utils import TDWUtils


"""
Add a custom fluid to the scene.
"""

c = Controller()
commands = [TDWUtils.create_empty_room(12, 12)]
# Add some blocks.
y = 0
x = -2
cube_scale = {"x": 0.2, "y": 0.2, "z": 0.4}
while y < 1:
    z = 0
    while z < 1:
        commands.extend(Controller.get_add_physics_object(model_name="cube",
                                                          object_id=Controller.get_unique_id(),
                                                          position={"x": x, "y": y, "z": z},
                                                          library="models_flex.json",
                                                          default_physics_values=False,
                                                          scale_factor=cube_scale,
                                                          scale_mass=False,
                                                          mass=1))
        z += cube_scale["z"]
    y += cube_scale["y"]
c.communicate(commands)
fluid_id = Controller.get_unique_id()
camera = ThirdPersonCamera(position={"x": 1.1, "y": 1.32, "z": -1.9},
                           look_at={"x": -2, "y": 0, "z": 0})
obi = Obi()
c.add_ons.extend([camera, obi])
obi.set_solver(gravity=TDWUtils.VECTOR3_ZERO)
# Define a custom fluid.
fluid = Fluid(capacity=10000,
              resolution=0.5,
              color={"r": 0, "g": 0, "b": 1, "a": 1},
              rest_density=1000,
              reflection=0,
              refraction=0,
              smoothing=2,
              render_smoothness=1,
              metalness=0,
              viscosity=0,
              absorption=0,
              vorticity=10,
              surface_tension=2.0,
              transparency=1.0,
              thickness_cutoff=100,
              radius_scale=1.5,
              random_velocity=0.125)
# Create the fluid.
obi.create_fluid(fluid=fluid,
                 shape=CubeEmitter(size={"x": 0.1, "y": 2, "z": 1}),
                 object_id=fluid_id,
                 position={"x": -0.1, "y": 0, "z": 0},
                 rotation={"x": 0, "y": -90, "z": 0},
                 lifespan=1,
                 speed=3)
for i in range(200):
    c.communicate([])
c.communicate({"$type": "set_obi_fluid_emitter",
               "id": fluid_id,
               "lifespan": 0.5,
               "speed": 0.5})
for i in range(100):
    c.communicate([])
c.communicate({"$type": "terminate"})
