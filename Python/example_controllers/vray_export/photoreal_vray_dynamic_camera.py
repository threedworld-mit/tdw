from tdw.controller import Controller
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.vray_export import VRayExport
from tdw.output_data import OutputData, AvatarTransformMatrices
from random import uniform



class PhotorealVRayDynamicCamera(Controller):
    """
    Create a photorealistic scene, focusing on post-processing and other effects.
    The "archviz_house" environment is used due to its maximal photorealistic lighting.
    """
    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.frame_range = 20

    def run(self):
        # Add a camera and enable image capture.
        camera = ThirdPersonCamera(avatar_id="a",
                                   position={"x": -3, "y": 1, "z": 0},
                                   look_at={"x": 0, "y": 1, "z": 0},
                                   field_of_view=55)
        export = VRayExport(image_width=1920, image_height=1080, scene_name="tdw_room", output_path="D:/VE2020_output/")
        self.add_ons.extend([camera, export])
        # Set the resolution to 1080p.
        # Set render quality to maximum.
        # Load the scene.
        # Add the objects.
        # Adjust post-processing parameters to achieve a suitable depth of field and exposure.
        # Also adjust the ambient occlusion parameters for realistic shadowing in corners and under furniture objects.
        # Set shadow strength to near-full.
        # Immediately end the simulation.
        self.communicate([{"$type": "set_screen_size",
                           "width": 1920,
                           "height": 1080},
                          {"$type": "set_render_quality",
                           "render_quality": 5},
                          self.get_add_scene(scene_name="tdw_room"),
                          self.get_add_object(model_name="live_edge_coffee_table",
                                              object_id=self.get_unique_id(),
                                              position={"x": 1.80, "y": 0, "z": 0},
                                              rotation={"x": 45, "y": 0, "z": 45}),
                         self.get_add_object(model_name="buddah",
                                              object_id=self.get_unique_id(),
                                              position={"x": 2.35, "y": 0, "z": 2},
                                              rotation={"x": 45, "y": 45, "z": 0}),
                         self.get_add_object(model_name="bastone_floor_lamp",
                                              object_id=self.get_unique_id(),
                                              position={"x": 2.0, "y": 0, "z": -1.5},
                                              rotation={"x": 0, "y": 0, "z": 0}),
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
                           "strength": 0.85}])
                          #{"$type": "terminate"}])
        # Download and unzip scene file -- this will be the "master" file, that all model .vrscene files will be appended to.
        export.download_scene()
        # Download and unzip all object models in the scene.
        export.download_scene_models()
        # Update model files to reflect scene object transforms.
        resp = self.communicate([])
        export.export_static_node_data(resp=resp)
        # Update V-Ray camera to reflect TDW camera position and orientation.
        resp = self.communicate([])
        export.export_static_camera_view_data(resp=resp)

        # Open the master scene file, so we can output the dynamic data for any moving objects, affected by applying the force.
        path = export.get_scene_file_path()      
        with open(path, "a") as f:        
            frame_count = 0
            for i in range(self.frame_range):
                resp = self.communicate({"$type": "teleport_avatar_to", "position": {"x": uniform(-3, -2), "y": uniform(0.5, 1.5), "z": uniform(-2, 2)}, "avatar_id": "a"})
                for i in range(len(resp) - 1):
                    r_id = OutputData.get_data_type_id(resp[i])
                    if r_id == "atrm":
                        avatar_transform_matrices = AvatarTransformMatrices(resp[i])
                        for j in range(avatar_transform_matrices.get_num()):
                            avatar_id = avatar_transform_matrices.get_id(j)
                            avatar_matrix = avatar_transform_matrices.get_avatar_matrix(j)
                            sensor_matrix = avatar_transform_matrices.get_sensor_matrix(j)
                            node_data_string = export.get_dynamic_camera_data(avatar_matrix, sensor_matrix, frame_count)
                            f.write(node_data_string)
                frame_count = frame_count + 1
            # Write out to the master scene file the final frame_count as the end of the animation sequence.
            export.export_animation_settings(frame_count)
        # Everything is prepared, now assemble the components by adding the models and view files to the scene file.
        #export.assemble_render_file()
        # Launch Vantage render with our assembled scene file.
        export.launch_vantage_render(start_frame=0, end_frame=frame_count)
        self.communicate({"$type": "terminate"})
        

if __name__ == "__main__":
    PhotorealVRayDynamicCamera(launch_build=False).run()
