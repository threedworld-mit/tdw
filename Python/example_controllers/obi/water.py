from tdw.controller import Controller
from tdw.add_ons.obi import Obi
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.obi_data.fluids.disk_emitter import DiskEmitter

"""
Pour water into a receptacle.
"""

c = Controller()
c.communicate(Controller.get_add_scene(scene_name="tdw_room"))
camera = ThirdPersonCamera(position={"x": -3.75, "y": 1.5, "z": -0.5},
                           look_at={"x": 0, "y": 0, "z": 0})
obi = Obi()
c.add_ons.extend([camera, obi])
obi.create_fluid(fluid="water",
                 shape=DiskEmitter(),
                 object_id=Controller.get_unique_id(),
                 position={"x": 0, "y": 2.35, "z": -1.5},
                 rotation={"x": 45, "y": 0, "z": 0},
                 speed=5)
c.communicate(Controller.get_add_physics_object(model_name="fluid_receptacle1x1",
                                                object_id=Controller.get_unique_id(),
                                                library="models_special.json",
                                                kinematic=True,
                                                gravity=False,
                                                scale_factor={"x": 2, "y": 2, "z": 2}))
for i in range(500):
    c.communicate([])
c.communicate({"$type": "terminate"})
