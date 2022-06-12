from tdw.controller import Controller
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.object_manager import ObjectManager
from requests import get
import os
import zipfile
import subprocess


class Photoreal(Controller):
    """
    Create a photorealistic scene, focusing on post-processing and other effects.
    The "archviz_house" environment is used due to its maximal photorealistic lighting.
    """
    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.S3_ROOT = "https://tdw-public.s3.amazonaws.com/vray_models/"
        self.PATH_ROOT = "D://VE2022_sandbox//"

    def run(self):
        # Add a camera and enable image capture.
        camera = ThirdPersonCamera(avatar_id="a",
                                   position={"x": -3, "y": 1.35, "z": -0.8},
                                   look_at={"x": 1.2, "y": 0.85, "z": -0.5},
                                   field_of_view=55)
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("photoreal")
        print(f"Image will be saved to: {path}")
        capture = ImageCapture(avatar_ids=["a"], path=path)
        self.add_ons.extend([camera, capture])
        om = ObjectManager(transforms=True, rigidbodies=False, bounds=False)
        self.add_ons.append(om)

        glass_table_id = self.get_unique_id()
        live_table_id = self.get_unique_id()
        chair_id = self.get_unique_id()
        lamp_id = self.get_unique_id()
        zen_id = self.get_unique_id()

        # Set the resolution to 1080p.
        # Set render quality to maximum.
        # Load the scene.
        # Add the objects.
        # Adjust post-processing parameters to achieve a suitable depth of field and exposure.
        # Also adjust the ambient occlusion parameters for realistic shadowing in corners and under furniture objects.
        # Set shadow strength to full.
        # Immediately end the simulation.
        self.communicate([{"$type": "set_screen_size",
                           "width": 1920,
                           "height": 1080},
                          {"$type": "set_render_quality",
                           "render_quality": 5},
                          self.get_add_scene(scene_name="tdw_room"),
                          self.get_add_object(model_name="glass_table",
                                              object_id=glass_table_id,
                                              position={"x":0.125, "y": 0, "z": 0.37},
                                              rotation={"x": 0, "y": 90, "z": 0}),
                          self.get_add_object(model_name="live_edge_coffee_table",
                                              object_id=live_table_id,
                                              position={"x": 1.81, "y": 0, "z": -0.47},
                                              rotation={"x": 0, "y": -90, "z": 0}),
                          self.get_add_object(model_name="bastone_floor_lamp",
                                              object_id=lamp_id,
                                              position={"x": 2.35, "y": 0, "z": 1},
                                              rotation={"x": 0, "y": 35, "z": 0}),
                          self.get_add_object(model_name="chair_eames_plastic_armchair",
                                              object_id=chair_id,
                                              position={"x": 0.9, "y": 0, "z": -1.615},
                                              rotation={"x": 0, "y": 63.25, "z": 0}),
                          self.get_add_object(model_name="zenblocks",
                                              object_id=zen_id,
                                              position={"x": 1.8, "y": 0.303, "z": -0.517},
                                              rotation={"x": 0, "y": 70, "z": 0}),
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
                           "strength": 1.0}])
                          #{"$type": "terminate"}])
        
        self.communicate([{"$type": "send_object_matrix", "id": glass_table_id},
                          {"$type": "send_object_matrix", "id": live_table_id},
                          {"$type": "send_object_matrix", "id": lamp_id},
                          {"$type": "send_object_matrix", "id": chair_id},
                          {"$type": "send_object_matrix", "id": zen_id}])
        
        for object_id in om.objects_static:
            #print(object_id, om.objects_static[object_id].name)
            self.download_zip(om.objects_static[object_id].name)
            print(om.objects_static[object_id].name + ", pos: " + str(om.transforms[object_id].position) + ", ori: " + str(om.transforms[object_id].rotation))
        
    
    def download_zip(self, model_name):
        """
        Download a model file and unzip into main "resources" folder
        """
        path = os.path.join(self.PATH_ROOT, model_name) + ".zip"
        url = os.path.join(self.S3_ROOT, model_name) + ".zip"
        with open(path, "wb") as f:
            f.write(get(url).content)
        # Unzip in place.
        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall(self.PATH_ROOT)
        # Delete the zip file.
        os.remove(path)


    def launch_vantage(self, scene_file, outfile):
        """
        Launch Vantage in headless mode and render scene file.
        """
        subprocess.run(["C://Program Files//Chaos Group//Vantage//vantage_console.exe", "-sceneFile=D://VE2022_sandbox//resources//" + scene_file, "-outputFile=D://VE2022_sandbox//" + outfile,  "-outputWidth=1280", "-outputHeight=720", "-quiet"])

if __name__ == "__main__":
    Photoreal(launch_build=False).run()
