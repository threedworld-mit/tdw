from tdw.controller import Controller
from tdw.add_ons.obi import Obi
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from random import uniform


"""
Minimal example of dropping a cloth sheet onto an object.
"""

c = Controller(launch_build=False)
c.communicate(Controller.get_add_scene(scene_name="tdw_room"))
cloth_id = Controller.get_unique_id()
receptacle_id = Controller.get_unique_id()
camera = ThirdPersonCamera(position={"x": -3.75, "y": 1.5, "z": -0.5},
                           look_at={"x": 0, "y": 1.25, "z": 0})
obi = Obi(output_data=False)
c.add_ons.extend([camera, obi])

# Create a sheet that looks and behaves like wool.
obi.create_cloth_sheet(name="silk_sheet",
                       cloth_material="canvas",
                       object_id=cloth_id,
                       position={"x": 0, "y": 1.5, "z": 0},
                       rotation={"x": 0, "y": 16.5, "z": 0},
                       sheet_type="cloth_hd",
                       solver_id=0)
c.communicate([{"$type": "set_screen_size",
                "width": 1920,
                "height": 1080},
               {"$type": "set_render_quality",
                "render_quality": 5}])
c.communicate([])
c.communicate([{"$type": "set_obi_solver_substeps",  "solver_id": 0, "substeps": 2},
               c.get_add_material(material_name="linen_burlap_irregular", library="materials_med.json"),
               {"$type": "set_obi_cloth_visual_material",  "id": cloth_id, "material_name": "linen_burlap_irregular", "scale": {"x":4, "y": 4}},
               {"$type": "set_obi_cloth_attachment",  "id": cloth_id, "group": "four_corners"}])

for i in range(500):
    c.communicate([])

for i in range(5):
    c.communicate(Controller.get_add_physics_object(model_name="sphere",
                                                object_id=Controller.get_unique_id(),
                                                library="models_flex.json",
                                                position={"x": uniform(-0.35, 0.35), "y": 1.5, "z": uniform(-0.35, 0.35)},
                                                default_physics_values=False,
                                                mass=uniform(0.25, 0.35),
                                                kinematic=False,
                                                gravity=True,
                                                scale_factor={"x":0.35, "y": 0.35, "z":0.35}))
for i in range(1000):
    c.communicate([])

c.communicate({"$type": "terminate"})