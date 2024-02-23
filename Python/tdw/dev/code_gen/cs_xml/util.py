from shutil import rmtree
from pathlib import Path
from os.path import join
from typing import List, Dict
import re
from xml.etree import ElementTree as Et
from tdw.dev.config import Config


def get_root(filename: str) -> Et.ElementTree:
    """
    Get the XML root of the file.

    :param filename: The .xml filename.
    """

    return Et.parse(join(XML_DIRECTORY, filename)).getroot()


def parse_para(tree: Et.Element) -> str:
    """
    Parse a string in the XML file that might have <para>.

    :param tree: The XML element tree.
    """

    output = ""
    # Add each paragraph.
    for para in tree.findall("para"):
        # Get raw inner text.
        raw = parse_ref(para)
        output += raw + " "
    return output.strip()


def parse_ref(element: Et.Element) -> str:
    """
    Remove all <ref> tags from an XML element.

    :param element: The element.
    """

    # Get raw inner text.
    raw = (element.text or '') + ''.join(Et.tostring(e, 'unicode') for e in element)
    # Strip reference tags.
    return re.sub("<ref(.*?)\">", "", raw).replace("</ref>", "")


def __get_py_enum_types() -> List[str]:
    from importlib import import_module
    from pathlib import Path
    from inflection import underscore
    enums = []
    for k in PY_IMPORT_TYPES:
        m = import_module(PY_IMPORT_TYPES[k])
        text = Path(f'{m.__path__[0]}/{underscore(k)}.py').read_text(encoding='utf-8')
        if 'from enum import' in text:
            enums.append(k)
    return enums


def recreate_directory(directory: Path) -> None:
    """
    Delete a directory and recreate it.

    :param directory: The directory.
    """

    if directory.exists():
        rmtree(str(directory.resolve()))
    directory.mkdir(parents=True)


CS_TO_PY_TYPES: Dict[str, str] = {"int?": "int",
                                  "string": "str",
                                  "string[]": "List[str]",
                                  "float[]": "List[float]",
                                  "int[]": "List[int]",
                                  "bool[]": "List[bool]",
                                  "List<string>": "List[str]",
                                  "List<float>": "List[float]",
                                  "List<int>": "List[int]",
                                  "List<bool>": "List[bool]",
                                  "Vector2": "Dict[str, float]",
                                  "Vector2Int": "Dict[str, int]",
                                  "Vector3": "Dict[str, float]",
                                  "Quaternion": "Dict[str, float]",
                                  "Vector3Int": "Dict[str, int]",
                                  "Vector3[]": "List[Dict[str, float]]",
                                  "Vector2Int[]": "List[Dict[str, float]]",
                                  "Color": "Dict[str, float]",
                                  "Trial[]": "List[Trial]",
                                  "CardinalDirection[]": "List[CardinalDirection]",
                                  "ImpactMaterialUnsized": "ImpactMaterial",
                                  "Vector4[]": "List[Dict[str, float]]",
                                  "ObiClothSheetType": "SheetType",
                                  "ObiClothVolumeType": "ClothVolumeType",
                                  "EmitterShapeBase": "EmitterShape",
                                  "Dictionary<TetherParticleGroup, TetherType>": "Dict[TetherParticleGroup, TetherType]",
                                  "VrRigType": "RigType",
                                  "ReplicantBodyPart[]": "List[ReplicantBodyPart]",
                                  "int[][]": "List[List[int]]",
                                  "CollisionType[]": "List[str]",
                                  "uint": "int",
                                  "List<PassMask>": "List[str]"}
STRS: List[str] = ["CarveType", "CarveShape", "SimpleBodyAvatar.SimpleBodyType", "AvatarType", "SurfaceMaterial",
                   "AudioEventType", "PrimitiveType", "LocalScene", "CarveShape", "Axis", "Frequency", "AntiAliasingMode",
                   "DetectionMode", "DriveAxis", "SemanticMaterialType", "AssetBundleType", "Shape", "TriggerShape"]
CS_TO_PY_DEFAULT_VALUES: Dict[str, str] = {"Color.red": '{"r": 1, "g": 0, "b": 0, "a": 1}',
                                           "Color.blue": '{"r": 0, "g": 0, "b": 1, "a": 1}',
                                           "Color.white": '{"r": 1, "g": 1, "b": 1, "a": 1}',
                                           "Color.black": '{"r": 0, "g": 0, "b": 0, "a": 1}',
                                           "Vector3.zero": '{"x": 0, "y": 0, "z": 0}',
                                           "Vector3.one": '{"x": 1, "y": 1, "z": 1}',
                                           "Vector3.forward": '{"x": 0, "y": 0, "z": 1}',
                                           "Vector2.one": '{"x": 1, "y": 1}',
                                           "Vector2.zero": '{"x": 0, "y": 0}',
                                           "Vector2Int.zero": '{"x": 0, "y": 0}',
                                           "Vector3Int.zero": '{"x": 0, "y": 0, "z": 0}',
                                           "Shape.sphere": "ContainerShape.sphere",
                                           "TriggerShape.cube": "TriggerColliderShape.cube",
                                           "VrRigType.oculus_touch_robot_hands": "RigType.oculus_touch_robot_hands",
                                           "ImpactMaterialUnsized.wood_medium": "ImpactMaterial.wood_medium",
                                           "AudioEventType.impact": '"impact"',
                                           "Quaternion.identity": '{"x": 0, "y": 0, "z": 0, "w": 1}'}
PY_TYPES: List[str] = ["str", "int", "float", "bool", "TrialAdder", "TrialStatus", "ContainerTag", "ScrapeMaterial",
                       "ForceMode", "ClothMaterial", "FluidBase", "ObiBackend", "Arm", "MaterialCombineMode",
                       "TetherParticleGroup", "TetherType", "Request"]
XML_DIRECTORY = str(Config().tdwunity_path.joinpath("Documentation/xml").resolve())
INDENT_4 = "    "
INDENT_8 = INDENT_4 + INDENT_4
INDENT_12 = INDENT_8 + INDENT_4
BUILTIN_TYPES: List[str] = ["str", "float", "int", "bool"]
PY_IMPORT_TYPES: Dict[str, str] = {"TrialAdder": "tdw.webgl.trial_adders",
                                   "TrialStatus": "tdw.webgl",
                                   "CardinalDirection": "tdw",
                                   "ContainerTag": "tdw.container_data",
                                   "ContainerShape": "tdw.container_data",
                                   "TriggerColliderShape": "tdw.collision_data",
                                   "Trial": "tdw.webgl.trials",
                                   "ImpactMaterial": "tdw.physics_audio",
                                   "ScrapeMaterial": "tdw.physics_audio",
                                   "ForceMode": "tdw.obi_data",
                                   "ClothMaterial": "tdw.obi_data.cloth",
                                   "SheetType": "tdw.obi_data.cloth",
                                   "TetherParticleGroup": "tdw.obi_data.cloth",
                                   "TetherType": "tdw.obi_data.cloth",
                                   "FluidBase": "tdw.obi_data.fluids",
                                   "EmitterShape": "tdw.obi_data.fluids",
                                   "ObiBackend": "tdw.obi_data",
                                   "RigType": "tdw.vr_data",
                                   "Arm": "tdw.replicant",
                                   "ReplicantBodyPart": "tdw.replicant",
                                   "MaterialCombineMode": "tdw.obi_data.collision_materials"}
PY_ENUM_TYPES: List[str] = __get_py_enum_types()
AUTOGENERATED: str = "# AUTOGENERATED FROM C#. DO NOT MODIFY."
COMMAND_TAGS: Dict[str, Dict[str, str]] = {"expensive": {"title": "Expensive",
                                                         "description": "This command is computationally expensive."},
                                           "deprecated": {"title": "Deprecated",
                                                          "description": "This command has been deprecated. In the next major TDW update (2.x.0), "
                                                                         "this command will be removed."},
                                           "send_data_once": {"title": "Sends data",
                                                              "description": "This command instructs the build to send output data.\n\n"
                                                                             "    - **Exactly once**\n\n"
                                                                             "    - **Type:** ?"},
                                           "send_data": {"title": "Sends data",
                                                         "description": "This command instructs the build to send output data.\n\n"
                                                                        "    - **Type:** ?"},
                                           "flex": {"title": "NVIDIA Flex",
                                                    "description": "This command initializes Flex, or requires Flex to be initialized."},
                                           "obi": {"title": "Obi",
                                                   "description": "This command initializes utilizes the Obi physics engine, which requires a specialized scene initialization process."},
                                           "debug": {"title": "Debug-only",
                                                     "description": "This command is only intended for use as a debug tool or diagnostic tool. "
                                                                    "It is not compatible with ordinary TDW usage."},
                                           "euler_angles": {"title": "Euler angles",
                                                            "description": "Rotational behavior can become unpredictable if the Euler angles of an "
                                                                           "object are adjusted more than once. Consider sending this command only to "
                                                                           "initialize the orientation."},
                                           "avatar_non_physics": {"title": "Non-physics motion",
                                                                  "description": "This command ignores the build's physics engine."
                                                                                 " If you send this command during a physics simulation "
                                                                                 "(i.e. to a non-kinematic avatar), the physics might glitch."},
                                           "avatar_physics": {"title": "Physics motion",
                                                              "description": "This command uses rigidbody physics. "
                                                                             "If you send this command to a kinematic avatar,"
                                                                             " nothing will happen. If you're running a physics simulation, "
                                                                             "you should _only_ send commands with this tag to move and rotate an avatar."},
                                           "vr": {"title": "VR",
                                                  "description": "This command will only work if you've already sent [create_vr_rig](create_vr_rig.md)."},
                                           "asset_bundle": {"title": "Downloads an asset bundle",
                                                            "description": "This command will download an asset bundle from TDW's asset bundle library. "
                                                                           "The first time this command is sent during a simulation, it will be slow "
                                                                           "(because it needs to download the file)."
                                                                           " Afterwards, the file data will be cached until the simulation is "
                                                                           "terminated, and this command will be much faster. "
                                                                           "See: ?"},
                                           "material": {"title": "Requires a material asset bundle",
                                                        "description": "To use this command, you must first download an load a material. "
                                                                       "Send the [add_material](add_material.md) command first."},
                                           "sub_object": {"title": "Sub-Object",
                                                          "description": "This command will only work with a sub-object of a Composite Object. "
                                                                         "The sub-object must be of the correct type. "
                                                                         "To determine which Composite Objects are currently in the scene, "
                                                                         "and the types of their sub-objects, "
                                                                         "send the [send_composite_objects](send_composite_objects.md) command.\n\n"
                                                                         "    - **Type:** ?"},
                                           "depth_of_field": {"title": "Depth of Field",
                                                              "description": "This command modifies the post-processing depth of field. "},
                                           "wrapper_function": {"title": "Wrapper function",
                                                                "description": "In TDW standalone, the Controller class has a wrapper function for this command that "
                                                                               "is usually easier than using the command itself."},
                                           "cached_in_memory": {"title": "Cached in memory",
                                                                "description": "When this object is destroyed, the asset bundle remains in memory."
                                                                               "If you want to recreate the object, the build will be able to "
                                                                               "instantiate it more or less instantly. To free up memory, send the "
                                                                               "command [unload_asset_bundles](unload_asset_bundles.md)."},
                                           "nav_mesh": {"title": "Requires a NavMesh",
                                                        "description": "This command requires a NavMesh."
                                                                       "Scenes created via [add_scene](add_scene.md) already have NavMeshes."
                                                                       "Proc-gen scenes don't; send [bake_nav_mesh](bake_nav_mesh.md) to create one."},
                                           "rare": {"title": "Rarely used",
                                                    "description": "This command is very specialized; "
                                                                   "it's unlikely that this is the command you want to use.\n\n"
                                                                   "    - **Use this command instead:** ?"},
                                           "towards": {"title": "Motion is applied over time",
                                                       "description": "This command will move, rotate, or otherwise adjust the avatar "
                                                                      "per-frame at a non-linear rate (smoothed at the start and end)."
                                                                      " This command must be sent per-frame to continuously update."},
                                           "replicant_motion": {"title": "Replicant motion",
                                                                "description": "This tells the Replicant to begin a motion. "
                                                                               "The Replicant will continue the motion per communicate() call "
                                                                               "until the motion is complete."},
                                           "replicant_status": {"title": "Replicant status",
                                                                "description": "This command will sometimes set the action status of the Replicant "
                                                                               "in the `Replicant` output data. This is usually desirable. "
                                                                               "In some cases, namely when you're calling several of these commands "
                                                                               "in sequence, you might want only the last command to set the status. "
                                                                               "See the `set_status` parameter, below."}}
CS_NAMESPACES = {'UnityEngine': ['Vector3', 'Vector3[]', 'Vector3Int', 'Vector2', 'Vector2Int', 'Quaternion', 'Color',
                                 'Vector4[]', 'Vector2Int[]', 'GameObject', 'Collider[]', 'MeshFilter[]', 'Renderer[]',
                                 'Transform[]', 'Dictionary<int, Transform>', 'Color32', 'ArticulationBody',
                                 'Quaternion[]', 'Rigidbody', 'ConfigurableJoint', 'HingeJoint', 'Light'],
                 'ProcGen': ['CardinalDirection[]'],
                 'FBOutput': ['List<PassMask>'],
                 'Clatter.Core': ['ImpactMaterialUnsized', 'ScrapeMaterial', 'AudioEventType'],
                 'TDW': ['List<ContainerShape>', 'CachedReplicantBodyPart[]', 'List<CachedSubObject>'],
                 'TDW.Obi': ['Dictionary<TetherParticleGroup, TetherType>', 'ClothMaterial', 'FluidBase',
                             'EmitterShapeBase'],
                 'TDW.Replicant': ['ReplicantBodyPart[]', 'HeldObject[]', 'ReplicantAnimation', 'WheelchairReplicant',
                                   'ReplicantCollisionListener'],
                 'TDW.Robotics': ['Magnebot'],
                 'RootMotion.FinalIK': ['LookAtIK', 'FullBodyBipedIK'],
                 'RootMotion': ['SolverManager[]'],
                 'System': ['Action'],
                 'PA_DronePack': ['PA_DroneController'],
                 'EVP': ['VehicleController'],
                 'System.Collections.Generic': ['Dictionary<int, ', 'Dictionary<GameObject, ']}
