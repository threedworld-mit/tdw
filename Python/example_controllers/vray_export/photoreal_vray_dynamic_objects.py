from tdw.controller import Controller
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.vray_export import VRayExport




class PhotorealVRay(Controller):
    """
    Create a photorealistic scene, focusing on post-processing and other effects.
    The "archviz_house" environment is used due to its maximal photorealistic lighting.
    """
    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.frame_range = 150
        self.chair_id = self.get_unique_id()
        self.table_id = self.get_unique_id()

    def run(self):
        # Add a camera and enable export.
        camera = ThirdPersonCamera(avatar_id="a",
                                   position={"x": -3, "y": 1, "z": 0},
                                   look_at={"x": 0, "y": 1, "z": 0},
                                   field_of_view=55)
        export = VRayExport(image_width=1280, 
                            image_height=720, 
                            scene_name="tdw_room", 
                            output_path="D:/VE2020_output/", 
                            animate=True,
                            local_render=False)
        self.add_ons.append(camera)
        # Set the resolution to 720p.
        # Set render quality to maximum.
        # Load the scene.
        # Add the objects.
        # Adjust post-processing parameters to achieve a suitable depth of field and exposure.
        # Also adjust the ambient occlusion parameters for realistic shadowing in corners and under furniture objects.
        # Set shadow strength to near-full.
        self.communicate([{"$type": "set_screen_size",
                           "width": 1280,
                           "height": 720},
                          {"$type": "set_render_quality",
                           "render_quality": 5},
                          {"$type": "set_aperture",
                           "aperture": 4.0},
                          {"$type": "set_focus_distance",
                           "focus_distance": 2.25},
                          {"$type": "set_post_exposure",
                           "post_exposure": 0.4},
                          {"$type": "set_ambient_occlusion_intensity",
                           "intensity": 0.175},
                          {"$type": "set_ambient_occlusion_thickness_modifier",
                           "thickness": 3.5},
                          {"$type": "set_shadow_strength",
                           "strength": 0.85},
                          self.get_add_scene(scene_name="tdw_room"),
                          self.get_add_object(model_name="coffee_table_glass_round",
                                              object_id=self.table_id,
                                              position={"x":0.125, "y": 0, "z": 0.37},
                                              rotation={"x": 0, "y": 45, "z": 0}),
                         self.get_add_object(model_name="live_edge_coffee_table",
                                              object_id=self.get_unique_id(),
                                              position={"x": 1.81, "y": 0, "z": -0.47},
                                              rotation={"x": 0, "y": -90, "z": 0}),
                         self.get_add_object(model_name="bastone_floor_lamp",
                                              object_id=self.get_unique_id(),
                                              position={"x": 2.35, "y": 0, "z": 1},
                                              rotation={"x": 0, "y": 35, "z": 0}),
                         self.get_add_object(model_name="chair_eames_plastic_armchair",
                                              object_id=self.chair_id,
                                              position={"x": 0.1, "y": 0, "z": 1.85},
                                              rotation={"x": 0, "y": 63.25, "z": 0}),
                         self.get_add_object(model_name="vase_05",
                                              object_id=self.get_unique_id(),
                                              position={"x": 0.125, "y": 0.3960, "z": 0.37},
                                              rotation={"x": 0, "y": 63.25, "z": 0}),
                         self.get_add_object(model_name="zenblocks",
                                              object_id=self.get_unique_id(),
                                              position={"x": 1.8, "y": 0.303, "z": -0.517},
                                              rotation={"x": 0, "y": 70, "z": 0})])
        for step in range(15):
            resp = self.communicate([])
        self.add_ons.append(export)
        for step in range(15):
            resp = self.communicate([])
        # Apply a force and run simulation for 150 frames.
        self.communicate({"$type": "apply_force_to_object",
                           "id": self.chair_id,
                           "force": {"x": 0, "y": 0.5, "z": -35}})
        for step in range(self.frame_range):
            resp = self.communicate([])
        

if __name__ == "__main__":
    PhotorealVRay(launch_build=False).run()
