from tdw.controller import Controller
from tdw.add_ons.obi import Obi
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.obi_data.fluids.cube_emitter import CubeEmitter
from tdw.obi_data.fluids.fluid import Fluid

"""
Add a custom fluid to the scene.
"""

c = Controller()
c.communicate(Controller.get_add_scene(scene_name="tdw_room"))
fluid_id = Controller.get_unique_id()
camera = ThirdPersonCamera(position={"x": 1.2, "y": 1.5, "z": -1.5},
                           look_at={"x": 0, "y": 0, "z": 0})
obi = Obi()
c.add_ons.extend([camera, obi])
fluid = Fluid(capacity=1500,
              resolution=1,
              color={"r": 0, "g": 1, "b": 0.5, "a": 0.8},
              rest_density=1000,
              reflection=0.25,
              refraction=0.034,
              smoothing=1.8,
              viscosity=0.001,
              vorticity=1,
              surface_tension=1,
              transparency=1)
obi.create_fluid(fluid=fluid,
                 shape=CubeEmitter(),
                 object_id=fluid_id,
                 position={"x": 0, "y": 2.35, "z": 0},
                 rotation={"x": 90, "y": 0, "z": 0},
                 speed=1)
c.communicate(Controller.get_add_physics_object(model_name="rh10",
                                                object_id=Controller.get_unique_id()))
for i in range(200):
    c.communicate([])
c.communicate({"$type": "terminate"})
