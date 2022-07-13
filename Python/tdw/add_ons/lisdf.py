from math import degrees
from typing import List, Union, Dict
from json import dumps
from pathlib import Path
import xml.etree.ElementTree
from platform import system
from tdw.add_ons.add_on import AddOn
from tdw.asset_bundle_creator import AssetBundleCreator
from tdw.tdw_utils import TDWUtils


class LISDF(AddOn):
    """
    Parse an [.lisdf file](https://learning-and-intelligent-systems.github.io/kitchen-worlds/tut-lisdf/).

    .lisdf models can't be directly added into TDW; they must first be converted into asset bundles. These asset bundles will be saved to the local disk, meaning that converting .lisdf data to asset bundles is a one-time process.

    Note that this is only a partial implementation of an .lisdf parser. More functionality will be added over time.

    When `read()` is called, asset bundles are automatically generated if they don't already exist. Then this add-on appends commands to the controller to add the objects to the scene.
    """

    def __init__(self):
        super().__init__()
        self.initialized = True

    def read(self, lisdf_path: Union[str, Path], output_directory: Union[str, Path], overwrite: bool = False,
             cleanup: bool = True, send_commands: bool = True, quiet: bool = False, display: str = ":0",
             unity_editor_path: Union[Path, str] = None) -> None:
        """
        Read an .lisdf file and send commands to the build to add the objects to the scene.
        If corresponding asset bundles don't exist in `asset_bundles_directory` or if `overwrite == True`, this function will call the `asset_bundle_creator` Unity project and generate new asset bundles.

        The resulting list of commands will be saved to `asset_bundles_directory/commands.json`. Optionally, they will also be sent to the build the next time `c.communicate()` is called.

        :param lisdf_path: The path to the .lisdf file as either a string or [`Path`](https://docs.python.org/3/library/pathlib.html).
        :param output_directory: The directory of the object asset bundles as either a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If it doesn't exist, it will be created while the .lisdf models are being converted.
        :param overwrite: If True, overwrite any asset bundles in `asset_bundles_directory`. If False, skip converting models if the asset bundles already exist.
        :param cleanup: If True, delete intermediary files such as .prefab files generated while creating asset bundles.
        :param send_commands: If True, the commands generated from the .lisdf file will be sent the next time `c.communicate()` is called.
        :param quiet: If True, don't print any messages to console.
        :param display: The display to launch Unity Editor on. Ignored if this isn't Linux.
        :param unity_editor_path: The path to the Unity Editor executable, for example `C:/Program Files/Unity/Hub/Editor/2020.3.24f1/Editor/Unity.exe`. If None, this script will try to find Unity Editor automatically.
        """

        if isinstance(lisdf_path, Path):
            src_str = str(lisdf_path.resolve())
            src_path = lisdf_path
        elif isinstance(lisdf_path, str):
            src_str = lisdf_path
            src_path = Path(lisdf_path)
        else:
            raise Exception(lisdf_path)
        if isinstance(output_directory, Path):
            dst_str = str(output_directory.resolve())
            dst_path = output_directory
        elif isinstance(output_directory, str):
            dst_str = output_directory
            dst_path = Path(output_directory)
        else:
            raise Exception(output_directory)
        if not dst_path.exists():
            dst_path.mkdir(parents=True)
        # Fix Windows paths.
        dst_str = dst_str.replace("\\", "/")
        src_str = src_str.replace("\\", "/")
        # Open the XML document.
        tree = xml.etree.ElementTree.parse(src_str)
        root = tree.getroot().find('world')
        commands = []
        # Add a camera.
        for child in root.findall("gui"):
            for gui_child in child:
                if gui_child.tag == "camera":
                    camera_position = TDWUtils.VECTOR3_ZERO
                    look_at = TDWUtils.VECTOR3_ZERO
                    for camera_child in gui_child:
                        if camera_child.tag == "xyz":
                            camera_position = TDWUtils.ros_position_to_vector3([float(v) for v in camera_child.text.split(" ")])
                        elif camera_child.tag == "point_to":
                            look_at = TDWUtils.ros_position_to_vector3([float(v) for v in camera_child.text.split(" ")])
                    # Add commands to create the avatar.
                    commands.extend(TDWUtils.create_avatar(position=camera_position,
                                                           avatar_id="a",
                                                           look_at=look_at))
        # Generate asset bundles if needed.
        args = [f'-path="{src_str}"',
                f'-output_directory="{dst_str}"']
        if overwrite:
            args.append("-overwrite")
        if cleanup:
            args.append("-cleanup")
        a = AssetBundleCreator(quiet=quiet, display=display, unity_editor_path=unity_editor_path)
        a.call_unity(class_name="LISDFImporter",
                     method="Read",
                     args=args)
        # Print the log.
        if not quiet:
            log_path = dst_path.joinpath("log.txt")
            if log_path.exists():
                print(log_path.read_text(encoding="utf-8"))
        # Record the model names and object IDs.
        models: Dict[str, int] = dict()
        object_id = 0
        for child in root.findall("model"):
            pose_node = child.find("pose")
            # Get the position and rotation.
            if pose_node is None:
                position = TDWUtils.VECTOR3_ZERO
                rotation = TDWUtils.VECTOR3_ZERO
            else:
                pose = [float(v) for v in pose_node.text.split(" ")]
                position = TDWUtils.ros_position_to_vector3(pose[:3])
                rotation = TDWUtils.ros_rpy_to_vector3(pose[3:])
            model_name = child.attrib["name"]
            # Check whether the asset bundle exists.
            asset_bundle_path = dst_path.joinpath(model_name).joinpath(system()).joinpath(model_name)
            if not asset_bundle_path.exists():
                if not quiet:
                    print(f"Warning! File not found: {asset_bundle_path}")
                continue
            # Record the object ID.
            models[model_name] = object_id
            # Add the command to create the object.
            commands.append({"$type": "add_object",
                             "name": model_name,
                             "url": f"file:///{str(asset_bundle_path.resolve())}",
                             "scale_factor": 1,
                             "position": position if position is not None else {"x": 0, "y": 0, "z": 0},
                             "rotation": rotation if rotation is not None else {"x": 0, "y": 0, "z": 0},
                             "category": "",
                             "id": object_id})
            # Increment the object ID.
            object_id += 1
        # Set joint poses.
        state_node = root.find("state")
        for model in state_node.findall("model"):
            # Get the object ID.
            robot_id = models[model.attrib["name"]]
            for joint in model.findall("joint"):
                commands.extend([{"$type": "set_joint_id",
                                  "joint_id": object_id,
                                  "id": robot_id},
                                 {"$type": "set_revolute_target",
                                  "target": degrees(float(joint.find("angle").text)),
                                  "joint_id": object_id,
                                  "id": robot_id}])
                object_id += 1
        # Dump the commands.
        dst_path.joinpath("commands.json").write_text(dumps(commands, indent=2))
        # Send the commands.
        if send_commands:
            self.commands.extend(commands)

    def on_send(self, resp: List[bytes]) -> None:
        pass

    def get_initialization_commands(self) -> List[dict]:
        return []
