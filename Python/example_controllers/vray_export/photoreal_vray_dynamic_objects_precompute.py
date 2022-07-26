from tdw.controller import Controller
from typing import List, Dict, Union
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.object_manager import ObjectManager
from tdw.add_ons.vray_export import VRayExport
from tdw.output_data import OutputData, TransformMatrices, SegmentationColors



class PhotorealVRay(Controller):
    """
    Create a photorealistic scene, focusing on post-processing and other effects.
    The "archviz_house" environment is used due to its maximal photorealistic lighting.
    """
    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        # Dictionary of object ID,,list of matrices. Used to store physics movement data, before we download
        # the V-Ray models and transform them.
        # Dictionary of model names by ID
        self.object_names: Dict[int, str] = dict()
        self.matrix_list: Dict(str, List(np.ndarray)) = dict()
        self.id_list = []
        self.frame_range = 100

    def add_objects(self, table_id, chair_id, load_scene: bool = True):
        if load_scene == True:
             self.communicate(self.get_add_scene(scene_name="tdw_room"))
        self.communicate([self.get_add_object(model_name="coffee_table_glass_round",
                                              object_id=table_id,
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
                                              object_id=chair_id,
                                              position={"x": 0.9, "y": 0, "z": -1.615},
                                              rotation={"x": 0, "y": 63.25, "z": 0}),
                         self.get_add_object(model_name="vase_05",
                                              object_id=self.get_unique_id(),
                                              position={"x": 0.125, "y": 0.3960, "z": 0.37},
                                              rotation={"x": 0, "y": 63.25, "z": 0}),
                         self.get_add_object(model_name="zenblocks",
                                              object_id=self.get_unique_id(),
                                              position={"x": 1.8, "y": 0.303, "z": -0.517},
                                              rotation={"x": 0, "y": 70, "z": 0})])
    def run(self):
        # Add a camera and enable image capture.
        camera = ThirdPersonCamera(avatar_id="a",
                                   position={"x": -3, "y": 1, "z": 0},
                                   look_at={"x": 0, "y": 1, "z": 0},
                                   field_of_view=55)
        table_id = self.get_unique_id()
        chair_id = self.get_unique_id()
        self.add_ons.append(camera)
        # Set the resolution to 1080p.
        # Set render quality to maximum.
        # Load the scene.
        # Add the objects.
        # Adjust post-processing parameters to achieve a suitable depth of field and exposure.
        # Also adjust the ambient occlusion parameters for realistic shadowing in corners and under furniture objects.
        # Set shadow strength to near-full.
        self.add_objects(table_id, chair_id, load_scene=True)
        self.communicate([{"$type": "send_transform_matrices",
                                     "frequency": "always"},
                          {"$type": "send_segmentation_colors",
                                    "frequency": "always"},
                          {"$type": "set_screen_size",
                           "width": 1920,
                           "height": 1080},
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
                           "strength": 0.85}])
        # Cache the names of th scene objects -- these will be the keys in the matrix dictionary.
        # We cannot use the object IDs,as they will change when we reset the scene.
        resp = self.communicate([])
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            # Get segmentation color output data.
            if r_id == "segm":
                segm = SegmentationColors(resp[i])
                for j in range(segm.get_num()):
                    # Cache the object names and IDs.
                    object_id = segm.get_object_id(j)
                    object_name = segm.get_object_name(j)
                    self.object_names[object_id] = object_name
        # Apply a force and run simulation for 100 frames, storing transform matrix data.
        self.communicate({"$type": "apply_force_to_object",
                           "id": chair_id,
                           "force": {"x": 0, "y": 0.5, "z": -10}})
        for step in range(100):
            resp = self.communicate([])
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                if r_id == "trma":
                    transform_matrices = TransformMatrices(resp[i])
                    # Iterate through the objects.
                    for j in range(transform_matrices.get_num()):
                        # Get the object ID.
                        object_id = transform_matrices.get_id(j)
                        mat = transform_matrices.get_matrix(j)
                        # Store the matrix for each object at this frame
                        object_name = self.object_names[int(object_id)]
                        if object_name in self.matrix_list.keys():
                            self.matrix_list[object_name].append(mat)
                        else: 
                            self.matrix_list[object_name] = []
                            self.matrix_list[object_name].append(mat)
        # Delete the objects, but not the camera. We will reload them right after to reset the scene.
        for id in self.object_names:
            self.communicate({"$type": "destroy_object", "id": int(id)})
        table_id = self.get_unique_id()
        chair_id = self.get_unique_id()
        # Reset the scene by reloading the objects, but not the scene itself.
        self.add_objects(table_id, chair_id, load_scene=False)
        # Now we create the V-Ray exporter add-on, which will initialize after we re-add the objects to the scene.
        export = VRayExport(image_width=1920, image_height=1080, scene_name="tdw_room", output_path="D:/VE2020_output/")
        self.add_ons.append(export)
        self.communicate([])
        """
        # Download and unzip scene file -- this will be the "master" file, that all model etc. .vrscene files will be appended to.
        export.download_scene()
        # Download and unzip all object models in the scene.
        export.download_scene_models()
        resp = self.communicate([])
        export.export_static_node_data(resp=resp)
        resp = self.communicate([])
        export.export_static_camera_view_data(resp=resp)
        """
        # Open the master scene file, so we can output the dynamic data for any moving objects, affected by applying the force.
        path = export.get_scene_file_path()      
        with open(path, "a") as f:        
            #while not om.rigidbodies[chair_id].sleeping:
            frame_count = 0
            for i in range(self.frame_range):
                for obj_name in self.matrix_list:
                    cached_mat = self.matrix_list[obj_name][i]
                    node_data_string = export.get_dynamic_node_data(cached_mat, obj_name, frame_count)
                    f.write(node_data_string)
                frame_count = frame_count + 1
        # Launch Vantage render with our final scene file.
        export.launch_render(start_frame=0, end_frame=frame_count)
        

if __name__ == "__main__":
    PhotorealVRay(launch_build=False).run()
