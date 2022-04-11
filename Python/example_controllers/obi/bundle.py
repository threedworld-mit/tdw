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
                       cloth_material="canvas",
                       object_id=cloth_id,
                       position={"x": 0, "y": 1.85, "z": 0},
                       rotation={"x": 0, "y": 0, "z": 0},
                       sheet_type="cloth_hd",
                       solver_id=0)
c.communicate([{"$type": "set_screen_size",
                "width": 1920,
                "height": 1080},
               {"$type": "set_render_quality",
                "render_quality": 5}])

#  Create the long bar-shaped attachment object.
c.communicate(Controller.get_add_physics_object(model_name="cube",
                                                object_id=receptacle_id,
                                                library="models_flex.json",
                                                position={"x": 0, "y": 1.85, "z": 0},
                                                kinematic=True,
                                                gravity=False,
                                                scale_factor={"x":0.05, "y": 0.05, "z":0.05}))

c.communicate([{"$type": "set_obi_solver_substeps",  "solver_id": 0, "substeps": 4},
               c.get_add_material(material_name="wool_tartan_multicolored", library="materials_med.json"),
               {"$type": "set_obi_cloth_visual_material",  "id": cloth_id, "material_name": "wool_tartan_multicolored", "scale": {"x":3, "y": 3}},
               {"$type": "set_obi_cloth_attachment",  "id": cloth_id, "object_id": receptacle_id, "group": "center"}])

# Let the cloth object settle.
for i in range(100):
    c.communicate([])

# Rotate the bar back and forth, moving the cloth with it.
for i in range(360):
   c.communicate({"$type": "rotate_object_by", "id": receptacle_id, "axis": "yaw", "is_world": False, "angle": 2})
   
for i in range(360):
   c.communicate({"$type": "rotate_object_by", "id": receptacle_id, "axis": "yaw", "is_world": False,  "angle": -2})

for i in range(1000):
    c.communicate([])

c.communicate({"$type": "terminate"})