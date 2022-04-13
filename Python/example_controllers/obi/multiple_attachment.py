from tdw.controller import Controller
from tdw.add_ons.obi import Obi
from tdw.add_ons.third_person_camera import ThirdPersonCamera



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

# Create a sheet that looks and behaves like canvas, that we will attach to a bar-shaped object.
# Note the offset in Z, required to line up the "north" edge of the sheet with the object.
obi.create_cloth_sheet(name="canvas_sheet",
                       cloth_material="plastic",
                       object_id=cloth_id,
                       position={"x": 1, "y": 1.0, "z": -1},
                       rotation={"x": 20, "y": 10, "z": 10},
                       sheet_type="cloth_hd",
                       solver_id=0)
c.communicate([{"$type": "set_screen_size",
                "width": 1920,
                "height": 1080},
               {"$type": "set_render_quality",
                "render_quality": 5}])

#  Create the long bar-shaped attachment object.
c.communicate(Controller.get_add_physics_object(model_name="sphere",
                                                object_id=receptacle_id,
                                                library="models_flex.json",
                                                position={"x": 1, "y": 3, "z": -1.35},
                                                default_physics_values=False,
                                                mass=0.25,
                                                kinematic=True,
                                                gravity=False,
                                                scale_factor={"x":0.35, "y": 0.35, "z":0.35}))
c.communicate([])
c.communicate([{"$type": "set_obi_solver_substeps",  "solver_id": 0, "substeps": 4},
               c.get_add_material(material_name="cotton_jean_light_blue", library="materials_med.json"),
               {"$type": "set_obi_cloth_visual_material",  "id": cloth_id, "material_name": "cotton_jean_light_blue", "scale": {"x":3, "y": 3}},
               {"$type": "set_obi_cloth_attachment",  "id": cloth_id, "group": "north_edge"},
               {"$type": "set_obi_cloth_attachment",  "id": cloth_id, "group": "south_edge"},
               {"$type": "set_obi_cloth_attachment",  "id": cloth_id, "group": "east_edge"},
               {"$type": "set_obi_cloth_attachment",  "id": cloth_id, "group": "west_edge"}])

# Let the cloth object settle.
for i in range(150):
    c.communicate([])

c.communicate([{"$type": "set_kinematic_state", "id": receptacle_id, "is_kinematic": False, "use_gravity": True},
               {"$type": "create_obi_colliders", "id": receptacle_id}])

for i in range(150):
    c.communicate([])

c.communicate({"$type": "terminate"})