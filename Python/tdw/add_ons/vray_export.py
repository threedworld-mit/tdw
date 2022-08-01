from typing import List, Dict, NamedTuple, Union
from tdw.add_ons.add_on import AddOn
from pathlib import Path
from tdw.output_data import OutputData, TransformMatrices, SegmentationColors, AvatarTransformMatrices, FieldOfView
from requests import get
import os
import re
import zipfile
import subprocess
import numpy as np


class matrix_data_struct(NamedTuple):
    column_one: str
    column_two: str
    column_three: str
    column_four: str


class VRayExport(AddOn):

    def __init__(self, image_width: int, image_height: int, scene_name: str, output_path: str, 
                 animate: bool = False, local_render: bool = True):
        super().__init__()
        self.output_path = output_path
        if not os.path.exists(self.output_path):
            os.mkdir(self.output_path)
        self.S3_ROOT = "https://tdw-public.s3.amazonaws.com/"
        self.VRAY_EXPORT_RESOURCES_PATH = Path.home().joinpath("vray_export_resources")
        if not self.VRAY_EXPORT_RESOURCES_PATH.exists():
            self.VRAY_EXPORT_RESOURCES_PATH.mkdir(parents=True)
        self.image_width: int = image_width
        self.image_height: int = image_height
        self.animate = animate
        self.scene_name = scene_name
        self.local_render = local_render
        # Conversion matrix from Y-up to Z-up, and left-hand to right-hand.
        self.handedness = np.array([[-1, 0, 0, 0],
                                    [0, 0, 1, 0],
                                    [0, -1, 0, 0],
                                    [0, 0, 0, 1]])
        # Conversion matrix for camera.
        self.camera_handedness = np.array([[1, 0, 0, 0],
                                           [0, 0, 1, 0],
                                           [0, -1, 0, 0],
                                           [0, 0, 0, 1]])
        self.anim_fix = np.array([[-1, 0, 0, 0],
                                  [0, 0, -1, 0],
                                  [0, -1, 0, 0],
                                  [0, 0, 0, 1]])
        # Dictionary of model names by ID
        self.object_names: Dict[int, str] = dict()
        # Dictionary of model IDs by name
        self.model_ids: Dict[str, int] = dict()
        # Dictionary of node IDs by model name
        self.node_ids: Dict[str, str] = dict()
        # The current frame count.
        self.frame_count: int = 0
        self.downloaded_data = False;


    def get_initialization_commands(self) -> List[dict]:
        commands = [{"$type": "send_transform_matrices",
                       "frequency": "always"},
                    {"$type": "send_segmentation_colors",
                       "frequency": "once"},
                    {"$type": "send_camera_matrices",
                       "frequency": "always"},
                    {"$type": "send_avatar_transform_matrices",
                      "frequency": "always"},
                    {"$type": "send_field_of_view",
                       "frequency": "always"}]
        return commands

    def rebuild_object_list(self, resp: List[bytes]) -> None:
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
                    self.model_ids[object_name] = object_id

    def on_send(self, resp: List[bytes]) -> None:
        """
        Perform all export processes except for initiating render. 
        Downloads master scene file, all object models, and exports all necessary data.
        """
        #Download the scene file and model files if we have not done so already.
        if not self.downloaded_data:
            self.downloaded_data = True;
            self.rebuild_object_list(resp=resp)       
            # Download and unzip scene file -- this will be the "master" file, that all model .vrscene files will be appended to.
            self.download_scene()
            # Download and unzip all object models in the scene.
            for model_name in self.object_names.values():
                self.download_model(model_name)
            # Update model files to reflect initial scene object transforms.
            self.export_static_node_data(resp=resp)
            # Update V-Ray camera to reflect TDW camera position and orientation.
            self.export_static_camera_view_data(resp=resp)
        # Process object or camera movement.
        if self.animate:
            self.export_animation(resp=resp)
        # Launch the Vantage render job.
        #if self.local_render:
            #self.launch_render()
        
    def get_scene_file_path(self) -> str:
        """
        Return the path to the downloaded master scene file.
        """
        path = os.path.join(self.VRAY_EXPORT_RESOURCES_PATH, self.scene_name) + ".vrscene"
        return path

    def download_model(self, model_name: str):
        """
        Download the zip file of a model from Amazon S3, and unpack the contents into the VRAY_EXPORT_RESOURCES_PATH folder.
        Delete the zip file.
        :param model_name: The name of the model.
        """
        path = os.path.join(self.VRAY_EXPORT_RESOURCES_PATH, model_name.lower())
        # Check if we have already downloaded this model. If so, just cache the node ID string for later use.
        # Otherwise download, unzip and cache the node ID string.
        if os.path.exists(path + ".vrscene"):
            node_id = self.get_node_id_string(model_name)
            self.node_ids[model_name] = node_id
        else:
            path = path + ".zip"
            url = os.path.join(self.S3_ROOT + "vray_models/", model_name.lower()) + ".zip"
            with open(path, "wb") as f:
                f.write(get(url).content)
            # Unzip in place.
            with zipfile.ZipFile(path, 'r') as zip_ref:
                zip_ref.extractall(self.VRAY_EXPORT_RESOURCES_PATH)
            # Delete the zip file.
            os.remove(path)
            # Cache the node ID string.
            node_id = self.get_node_id_string(model_name)
            self.node_ids[model_name] = node_id

    def download_scene(self):
        """
        Download the zip file of a streamed scene from Amazon S3, and unpack the contents into the general "resources" folder.
        :param model_name: The name of the scene.
        """
        path = os.path.join(self.VRAY_EXPORT_RESOURCES_PATH, self.scene_name) + ".zip"
        url = os.path.join(self.S3_ROOT + "vray_scenes/", self.scene_name) + ".zip"
        with open(path, "wb") as f:
            f.write(get(url).content)
        # Unzip in place.
        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall(self.VRAY_EXPORT_RESOURCES_PATH)
        # Delete the zip file.
        os.remove(path)

    def get_node_id_string(self, model_name: str) -> str:
        """
        For a given model (name), get the full Node ID string associated with that model.
        :param model_name: The name of the model.
        """
        path = os.path.join(self.VRAY_EXPORT_RESOURCES_PATH, model_name)  + ".vrscene"
        with open(path, "r") as filename:  
            # Look for Node structure and output node ID.
            src_str = model_name + "@node_"
            pattern = re.compile(src_str, re.IGNORECASE)
            for line in filename:
                if pattern.search(line):
                    return line

    def get_renderview_id_string(self) -> str:
        """
        Get the full ID string associated with the RenderView entry in the scene file.
        """
        path = self.get_scene_file_path()
        with open(path, "r") as filename:  
            # Look for Node structure and output node ID.
            src_str = "RenderView"
            pattern = re.compile(src_str)
            for line in filename:
                if pattern.search(line):
                    return line

    def get_renderview_line_number(self):
        """
        Get the line number of the RenderView entry in the scene file.
        """
        path = self.get_scene_file_path()
        node_line_number = 0
        num = 0
        with open(path, "r", encoding="utf-8") as in_file:
            pattern = re.compile("RenderView")
            for line in in_file:
                if pattern.search(line):
                    # We will want to replace the line following the "RenderView" line, with the transform data
                    node_line_number = num + 1
                    return node_line_number
                else:
                    num = num + 1

    def get_focal_length_line_number(self):
        """
        Get the line number of the CameraPhysical entry in the scene file.
        """
        path = self.get_scene_file_path()
        focal_line_number = 0
        num = 0
        with open(path, "r", encoding="utf-8") as in_file:
            pattern = re.compile("CameraPhysical")
            for line in in_file:
                if pattern.search(line):
                    # We will want to replace the third line following the "CameraPhysical" line, with the TDW focal length.
                    focal_line_number = num + 3
                    return focal_line_number
                else:
                    num = num + 1

    def write_static_node_data(self, model_name: str, mat: matrix_data_struct):
        """
        Replace the Node transform in a model's .vrscene file to match the object's position 
        and orientation in the TDW scene.
        """
        # get node ID from cached dictionary.
        node_id_string = self.node_ids[model_name]
        # Open model .vrscene file to append node data
        path = os.path.join(self.VRAY_EXPORT_RESOURCES_PATH, model_name)  + ".vrscene"
        node_string = ("transform=Transform(Matrix" + 
                      "(Vector(" + mat.column_one + "), " +
                      "Vector(" + mat.column_two + "), " +
                      "Vector(" + mat.column_three + ")), " +
                      "Vector(" + mat.column_four + "));\n")
        """
        node_string = ("\n" + node_id_string + 
                       "transform=interpolate(\n" +
                       "(0, Transform(Matrix" + 
                       "(Vector(" + mat.column_one + "), " +
                       "Vector(" + mat.column_two + "), " +
                       "Vector(" + mat.column_three + ")), " +
                       "Vector(" + mat.column_four + "))),\n" +
                       "(1, Transform(Matrix" + 
                       "(Vector(" + mat.column_one + "), " +
                       "Vector(" + mat.column_two + "), " +
                       "Vector(" + mat.column_three + ")), " +
                       "Vector(" + mat.column_four + ")))\n" +
                       ");\n}\n")
        """
        line_number = 0
        num = 0
        with open(path, "r", encoding="utf-8") as in_file:
            pattern = re.compile(node_id_string)
            for line in in_file:
                if pattern.search(line):
                    # We will want to replace the line following the "Node" line, with the transform data
                    line_number = num + 1
                else:
                    num = num + 1
            # Read file lines into data
            in_file.seek(0)
            data = in_file.readlines()
            # Now change the Node Transform line
            data[line_number] = node_string
        # Write everything back
        with open(path, 'w', encoding="utf-8") as out_file:
           out_file.writelines(data)

    def write_camera_param_data(self, mat: matrix_data_struct, focal: float):
        """
        Replace the camera transform line in the scene file with the converted TDW camera pos/ori data.
        Replace the physical camera focal length line in the scene file with the TDW focal length.
        """
        # Open model .vrscene file to append node data
        path = self.get_scene_file_path()
        node_string = ("transform=Transform(Matrix" + 
                       "(Vector(" + mat.column_one + "), " +
                       "Vector(" + mat.column_two + "), " +
                       "Vector(" + mat.column_three + ")), " +
                       "Vector(" + mat.column_four + "));\n")
        node_line_number = self.get_renderview_line_number()
        focal_line_number = self.get_focal_length_line_number()
        with open(path, 'r', encoding="utf-8") as in_file:
            # Read a list of lines into data
            data = in_file.readlines()
            # Now change the Renderview node line and the CameraPhysical focal_length line.
            data[node_line_number] = node_string
            data[focal_line_number] = "focal_length=" + str(focal) + ";\n"
        # Write everything back
        with open(path, 'w', encoding="utf-8") as out_file:
           out_file.writelines(data)

    def pre_rotate_models(self):
        for object_id in self.object_names:
            self.commands.append({"$type": "rotate_object_by", "angle": 180.0, "id": int(object_id), "axis": "pitch", "is_world": False, "use_centroid": False})

    def pre_rotate_model(self, object_name):
        object_id = self.model_ids[object_name]
        self.commands.append({"$type": "rotate_object_by", "angle": 180.0, "id": int(object_id), "axis": "pitch", "is_world": False, "use_centroid": False})

    def export_static_node_data(self, resp: List[bytes]):
        """
        For each model in the scene, export the position and orientation data to the model's .vrscene file as Node data.
        Then append an #include reference to the model file at the end of the main scene file.
        """
        self.rebuild_object_list(resp)
        path = self.get_scene_file_path()
        with open(path, "a") as f: 
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                if r_id == "trma":
                    transform_matrices = TransformMatrices(resp[i])
                    # Iterate through the objects.
                    for j in range(transform_matrices.get_num()):
                        # Get the object ID.
                        object_id = transform_matrices.get_id(j) 
                        # Get the matrix and convert it.
                        # Equivalent to: handedness * object_matrix * handedness.
                        matrix = np.matmul(self.handedness, np.matmul(transform_matrices.get_matrix(j), self.handedness))
                        # Note that V-Ray units are in centimeters while Unity's are in meters, so we need to multiply the position values by 100.
                        pos_x = (matrix[3][0] * 100)
                        pos_y = (matrix[3][1] * 100)
                        pos_z = (matrix[3][2] * 100)
                        mat_struct = matrix_data_struct(column_one = str(matrix[0][0]) + "," + str(matrix[0][1]) + "," + str(matrix[0][2]), 
                                                        column_two = str(matrix[1][0]) + "," + str(matrix[1][1]) + "," + str(matrix[1][2]), 
                                                        column_three = str(matrix[2][0]) + "," + str(matrix[2][1]) + "," + str(matrix[2][2]),  
                                                        column_four = str(pos_x) + "," + str(pos_y) + "," + str(pos_z))
                        # Get the model name for this ID
                        model_name = self.object_names[object_id]
                        self.write_static_node_data(model_name, mat_struct)
                        f.write("#include \"" + model_name + ".vrscene\"\n\n")

    def get_dynamic_node_data(self, mat, model_name: str, frame_count: int) -> str:
        """
        For each model in the scene, compute the position and orientation data for one frame, as Node data.
        Return a per-frame interpolated Node data string of the form:
        Node Box102@node_9701 {
          transform=interpolate(
          (2, Transform(Matrix(Vector(1, 0, 0), Vector(0, 1, 0), Vector(0, 0, 1)), Vector(-152.2906646728516, -145.2715454101563, 0)))
          );
        }
        For each frame in the object's motion, we will output one of these strings that interpolates from the previous frame
        to the new frame's transform matrix values.
        """
        # Get the matrix and convert it.
        # Equivalent to: handedness * object_matrix * handedness.
        matrix = np.matmul(self.anim_fix, np.matmul(mat, self.anim_fix))
        # Note that V-Ray units are in centimeters while Unity's are in meters, so we need to multiply the position values by 100.
        pos_x = (matrix[3][0] * 100)
        pos_y = (matrix[3][1] * 100)
        pos_z = -(matrix[3][2] * 100)
        mat_struct = matrix_data_struct(column_one = str(matrix[0][0]) + "," + str(matrix[0][1]) + "," + str(matrix[0][2]), 
                                        column_two = str(matrix[1][0]) + "," + str(matrix[1][1]) + "," + str(matrix[1][2]), 
                                        column_three = str(matrix[2][0]) + "," + str(matrix[2][1]) + "," + str(matrix[2][2]),  
                                        column_four = str(pos_x) + "," + str(pos_y) + "," + str(pos_z))
        # Get node ID from cached dictionary.
        node_id_string = self.node_ids[model_name]
        # Form interpolation string.
        node_string = ("\n" + node_id_string + 
                      "transform=interpolate(\n" +
                      "(" + str(frame_count) + ", " +
                      "Transform(Matrix" + 
                      "(Vector(" + mat_struct.column_one + "), " +
                      "Vector(" + mat_struct.column_two + "), " +
                      "Vector(" + mat_struct.column_three + ")), " +
                      "Vector(" + mat_struct.column_four + ")))\n" +
                      ");\n}\n")
        return node_string

    def export_static_camera_view_data(self, resp: List[bytes]):
        """
        Export the position and orientation of the camera to the scene .vrscene file as Transform data.
        """	
        focal = 0
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "fofv":
                field_of_view = FieldOfView(resp[i])
                focal = field_of_view.get_focal_length()
            if r_id == "atrm":
                avatar_transform_matrices = AvatarTransformMatrices(resp[i])
                for j in range(avatar_transform_matrices.get_num()):
                    avatar_id = avatar_transform_matrices.get_id(j)
                    avatar_matrix = avatar_transform_matrices.get_avatar_matrix(j)
                    sensor_matrix = avatar_transform_matrices.get_sensor_matrix(j)
                    # Get the matrix and convert it.
                    # Equivalent to: handedness * object_matrix * handedness.
                    pos_matrix = np.matmul(self.camera_handedness, np.matmul(avatar_matrix, self.camera_handedness))
                    rot_matrix = np.matmul(sensor_matrix, self.camera_handedness)
                    #rot_matrix = np.matmul(rot_matrix, self.camera_fix)
                    # Note that V-Ray units are in centimeters while Unity's are in meters, so we need to multiply the position values by 100.
                    # We also need to negate the X value, to complete the handedness conversion.
                    pos_x = -(pos_matrix[3][0] * 100)
                    pos_y = (pos_matrix[3][1] * 100)
                    pos_z = (pos_matrix[3][2] * 100)
                    mat_struct = matrix_data_struct(column_one = str(rot_matrix[0][0]) + "," + str(rot_matrix[0][1]) + "," + str(rot_matrix[0][2]), 
                                                    column_two = str(rot_matrix[1][0]) + "," + str(rot_matrix[1][1]) + "," + str(rot_matrix[1][2]), 
                                                    column_three = str(rot_matrix[2][0]) + "," + str(rot_matrix[2][1]) + "," + str(rot_matrix[2][2]),  
                                                    column_four = str(pos_x) + "," + str(pos_y) + "," + str(pos_z))
        self.write_camera_param_data(mat_struct, focal)


    def get_dynamic_camera_data(self, avatar_matrix, sensor_matrix, frame_count: int) -> str:
        """
        Compute the position and orientation of the camera for one frame, as Node data.
        Return a per-frame interpolated Node data string of the form:
        Node Box102@node_9701 {
          transform=interpolate(
          (2, Transform(Matrix(Vector(1, 0, 0), Vector(0, 1, 0), Vector(0, 0, 1)), Vector(-152.2906646728516, -145.2715454101563, 0)))
          );
        }
        For each frame in the camera's motion, we will output one of these strings that interpolates from the previous frame
        to the new frame's transform matrix values.
        """
        # Get the matrix and convert it.
        # Equivalent to: handedness * object_matrix * handedness.
        pos_matrix = np.matmul(self.camera_handedness, np.matmul(avatar_matrix, self.camera_handedness))
        rot_matrix = np.matmul(sensor_matrix, self.camera_handedness)
        # Note that V-Ray units are in centimeters while Unity's are in meters, so we need to multiply the position values by 100.
        # We also need to negate the X value, to complete the handedness conversion.
        pos_x = -(pos_matrix[3][0] * 100)
        pos_y = (pos_matrix[3][1] * 100)
        pos_z = (pos_matrix[3][2] * 100)
        mat_struct = matrix_data_struct(column_one = str(rot_matrix[0][0]) + "," + str(rot_matrix[0][1]) + "," + str(rot_matrix[0][2]), 
                                        column_two = str(rot_matrix[1][0]) + "," + str(rot_matrix[1][1]) + "," + str(rot_matrix[1][2]), 
                                        column_three = str(rot_matrix[2][0]) + "," + str(rot_matrix[2][1]) + "," + str(rot_matrix[2][2]),  
                                        column_four = str(pos_x) + "," + str(pos_y) + "," + str(pos_z))
        node_id_string = self.get_renderview_id_string()
        # Form interpolation string.
        node_string = ("\n" + node_id_string + 
                      "transform=interpolate(\n" +
                      "(" + str(frame_count) + ", " +
                      "Transform(Matrix" + 
                      "(Vector(" + mat_struct.column_one + "), " +
                      "Vector(" + mat_struct.column_two + "), " +
                      "Vector(" + mat_struct.column_three + ")), " +
                      "Vector(" + mat_struct.column_four + ")))\n" +
                      ");\n}\n")
        return node_string
   
    def export_animation_settings(self, end_frame: int):
        """
        Write out the output settings with the end frame of any animation in the scene.
        """
        path = self.get_scene_file_path()
        with open(path, "a") as f:
            out_string = ("SettingsOutput output_settings {\n" + 
                         "img_width=" + str(self.image_width) + ";\n" + 
                         "img_height=" + str(self.image_height) + ";\n" + 
                         "img_pixelAspect=1;\n" + 
                         "img_file_needFrameNumber=1;\n" + 
                         "img_clearMode=0;\n" + 
                         "anim_start=0;\n" + 
                         "anim_end=" + str(end_frame) + ";\n" + 
                         "frame_start=0;\n" +
                         "frames_per_second=1;\n" +
                         "frames=List(\n" + 
                         "List(0, " + str(end_frame) + ")\n" + 
                         ");\n" + 
                         "}\n")
            f.write(out_string)


    def export_animation(self, resp: List[bytes]):
        """
        
        """
        # Open the master scene file, so we can output the dynamic data for any moving objects and/or a moving camera.
        path = self.get_scene_file_path()      
        with open(path, "a") as f:                
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                if r_id == "atrm":
                    avatar_transform_matrices = AvatarTransformMatrices(resp[i])
                    for j in range(avatar_transform_matrices.get_num()):
                        avatar_id = avatar_transform_matrices.get_id(j)
                        avatar_matrix = avatar_transform_matrices.get_avatar_matrix(j)
                        sensor_matrix = avatar_transform_matrices.get_sensor_matrix(j)
                        # Convert matrices to V-Ray format and output to master scene file as frame-by-frame interpolations.
                        node_data_string = self.get_dynamic_camera_data(avatar_matrix, sensor_matrix, self.frame_count)
                        f.write(node_data_string)
                if r_id == "trma":
                    transform_matrices = TransformMatrices(resp[i])
                    # Iterate through the objects.
                    for j in range(transform_matrices.get_num()):
                        # Get the object ID.
                        object_id = transform_matrices.get_id(j)
                        mat = transform_matrices.get_matrix(j)
                        node_data_string = self.get_dynamic_node_data(mat, self.object_names[object_id], self.frame_count)
                        f.write(node_data_string)
            self.frame_count += 1


    def assemble_render_file(self):
        """
        If Node and/or Lights dynamic data was exported, append to the end of the master scene file.
        """
        scene_path = self.get_scene_file_path()
        with open(scene_path, "a") as f:  
            #f.write("#include models.vrscene\n")
            #f.write("#include views.vrscene\n")
            # Append nodes and lights files also, if either one exists
            if os.path.exists("nodes.vrscene"):
                f.write("#include nodes.vrscene\n")
            if os.path.exists("lights.vrscene"):
                f.write("#include lights.vrscene\n")

    def launch_render(self):
        """
        Launch Vantage in headless mode and render scene file, updating for animation if necessary.
        """
        # Open the master scene file.
        scene_path = self.get_scene_file_path()
        output_path = str(self.output_path) + self.scene_name + ".png"
        #os.chmod("C://Program Files//Chaos Group//Vantage//vantage_console.exe", 0o777)
        if self.frame_count > 0:
            # Write out to the master scene file the final frame_count as the end of the animation sequence.
            self.export_animation_settings(self.frame_count)
            # Launch vantage in appropriate mode.
            subprocess.run(["C:/Program Files/Chaos Group/Vantage/vantage.exe", 
                        "-sceneFile=" + scene_path, 
                        "-outputFile=" + output_path,  
                        "-outputWidth=" + str(self.image_width), 
                        "-outputHeight=" + str(self.image_height),
                        "-frames=0" + "-" + str(self.frame_count),
                        "-quiet",
                        "-autoClose=true"])
        else:
            subprocess.run(["C:/Program Files/Chaos Group/Vantage/vantage.exe", 
                        "-sceneFile=" + scene_path, 
                        "-outputFile=" + output_path,  
                        "-outputWidth=" + str(self.image_width), 
                        "-outputHeight=" + str(self.image_height),
                        "-quiet",
                        "-autoClose=true"])

	