from tdw.controller import Controller
from tdw.add_ons.obi import Obi
from tdw.add_ons.third_person_camera import ThirdPersonCamera



"""
Minimal example of dropping a cloth sheet onto an object.
"""

c = Controller(launch_build=False)
c.communicate(Controller.get_add_scene(scene_name="tdw_room"))
cloth_id = Controller.get_unique_id()
sphere_1_id = Controller.get_unique_id()
sphere_2_id = Controller.get_unique_id()
sphere_3_id = Controller.get_unique_id()
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

c.communicate(Controller.get_add_physics_object(model_name="sphere",
                                                object_id=sphere_1_id,
                                                library="models_flex.json",
                                                position={"x": 0.5, "y": 2.5, "z": 0.5},
                                                default_physics_values=False,
                                                mass=0.35,
                                                kinematic=True,
                                                gravity=False,
                                                scale_factor={"x":0.25, "y": 0.25, "z":0.25}))
c.communicate(Controller.get_add_physics_object(model_name="sphere",
                                                object_id=sphere_2_id,
                                                library="models_flex.json",
                                                position={"x": -0.5, "y": 2.0, "z": 0.35},
                                                default_physics_values=False,
                                                mass=0.4,
                                                kinematic=True,
                                                gravity=False,
                                                scale_factor={"x":0.3, "y": 0.3, "z":0.3}))
c.communicate(Controller.get_add_physics_object(model_name="sphere",
                                                object_id=sphere_3_id,
                                                library="models_flex.json",
                                                position={"x": -0.5, "y": 1.5, "z": -0.5},
                                                default_physics_values=False,
                                                mass=0.25,
                                                kinematic=True,
                                                gravity=False,
                                                scale_factor={"x":0.35, "y": 0.35, "z":0.35}))

c.communicate([{"$type": "set_obi_solver_substeps",  "solver_id": 0, "substeps": 3},
               c.get_add_material(material_name="linen_burlap_irregular", library="materials_med.json"),
               {"$type": "set_obi_cloth_visual_material",  "id": cloth_id, "material_name": "linen_burlap_irregular", "scale": {"x":4, "y": 4}},
               {"$type": "set_obi_cloth_attachment",  "id": cloth_id, "group": "four_corners"}])

for i in range(500):
    c.communicate([])

c.communicate([{"$type": "set_kinematic_state", "id": sphere_1_id, "is_kinematic": False, "use_gravity": True},
               {"$type": "set_kinematic_state", "id": sphere_2_id, "is_kinematic": False, "use_gravity": True},
               {"$type": "set_kinematic_state", "id": sphere_3_id, "is_kinematic": False, "use_gravity": True},
               {"$type": "create_obi_colliders", "id": sphere_1_id},
               {"$type": "create_obi_colliders", "id": sphere_2_id},
               {"$type": "create_obi_colliders", "id": sphere_3_id}])

for i in range(1000):
    c.communicate([])

c.communicate({"$type": "terminate"})