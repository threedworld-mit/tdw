import json
from typing import List, Dict, TypeVar, Union, Generic, Optional, Tuple
import pkg_resources
from pathlib import Path
import platform
from secrets import token_hex
from tdw.collision_data.trigger_collider_shape import TriggerColliderShape
from tdw.scene_data.room import Room
from tdw.scene_data.interior_region import InteriorRegion
from tdw.container_data.container_tag import ContainerTag
from tdw.container_data.container_shape import ContainerShape
from tdw.container_data.box_container import BoxContainer
from tdw.container_data.sphere_container import SphereContainer
from tdw.container_data.cylinder_container import CylinderContainer


class _Encoder(json.JSONEncoder):
    """
    JSON encoder for misc. record data.
    """

    def default(self, obj):
        if isinstance(obj, ContainerTag):
            return obj.name
        elif isinstance(obj, TriggerColliderShape):
            return obj.name
        elif isinstance(obj, BoxContainer):
            c = {"shape": TriggerColliderShape.box.name}
            c.update(obj.__dict__)
            return c
        elif isinstance(obj, SphereContainer):
            c = {"shape": TriggerColliderShape.sphere.name}
            c.update(obj.__dict__)
            return c
        elif isinstance(obj, CylinderContainer):
            c = {"shape": TriggerColliderShape.cylinder.name}
            c.update(obj.__dict__)
            return c
        elif isinstance(obj, Room):
            return obj.__dict__
        elif isinstance(obj, InteriorRegion):
            return {"region_id": obj.region_id, "center": list(obj.center), "bounds": list(obj.bounds),
                    "non_continuous_walls": obj.non_continuous_walls, "walls_with_windows": obj.walls_with_windows}
        else:
            return super(_Encoder, self).default(obj)


class _Record:
    """
    Abstract class for a metadata record.
    """

    _PLATFORM = platform.system()

    def __init__(self, data: Optional[dict] = None):
        """
        :param data: JSON data for the record. If None, the record will initialize with default values.
        """

        if data is None:
            self.name: str = ""
            self.urls: Dict[str, str] = {"Windows": "", "Darwin": "", "Linux": ""}
        else:
            self.name = data["name"]
            self.urls: Dict[str, str] = data["urls"]

    def get_url(self) -> str:
        """
        Returns the URL of the asset bundle for this platform. This is a wrapper for record.urls.
        """

        return self.urls[_Record._PLATFORM]

    def get_serializable(self) -> dict:
        """
        Returns the serializable dictionary of this record.
        """

        return self.__dict__


class ModelRecord(_Record):
    """
    A record of a model asset bundle.
    """

    def __init__(self, data: Optional[dict] = None):
        super().__init__(data)

        if data is None:
            self.wnid: str = ""
            self.wcategory: str = ""
            self.scale_factor: float = 1
            self.do_not_use: bool = False
            self.do_not_use_reason: str = ""
            self.flex: bool = False
            self.substructure: List[dict] = []
            self.bounds: Dict[str, Dict[str, float]] = {"back": {"x": 0, "y": 0, "z": 0},
                                                        "bottom": {"x": 0, "y": 0, "z": 0},
                                                        "center": {"x": 0, "y": 0, "z": 0},
                                                        "front": {"x": 0, "y": 0, "z": 0},
                                                        "left": {"x": 0, "y": 0, "z": 0},
                                                        "right": {"x": 0, "y": 0, "z": 0},
                                                        "top": {"x": 0, "y": 0, "z": 0}}
            self.canonical_rotation: Dict[str, float] = {"x": 0, "y": 0, "z": 0}
            self.physics_quality: float = -1
            self.asset_bundle_sizes: Dict[str, int] = {"Windows": -1, "Darwin": -1, "Linux": -1}
            self.composite_object = False
            self.container_shapes: List[ContainerShape] = list()
            self.affordance_points: List[Dict[str, float]] = list()
        else:
            self.wnid: str = data["wnid"]
            self.wcategory: str = data["wcategory"]
            self.scale_factor: float = data["scale_factor"]
            self.do_not_use: bool = data["do_not_use"]
            self.do_not_use_reason: str = data["do_not_use_reason"]
            self.flex: bool = data["flex"]
            self.substructure: List[dict] = data["substructure"]
            self.bounds: Dict[str, Dict[str, float]] = data["bounds"]
            self.canonical_rotation: Dict[str, float] = data["canonical_rotation"]
            self.physics_quality: float = data["physics_quality"]
            self.asset_bundle_sizes: Dict[str, int] = data["asset_bundle_sizes"]
            self.composite_object: bool = data["composite_object"]
            if "volume" not in data:
                self.volume: float = 0
            else:
                self.volume: float = data["volume"]
            self.container_shapes: List[ContainerShape] = list()
            if "container_shapes" in data:
                for container in data["container_shapes"]:
                    shape = TriggerColliderShape[container["shape"]]
                    tag = ContainerTag[container["tag"]]
                    if shape == TriggerColliderShape.box:
                        obj = BoxContainer(tag=tag,
                                           position=container["position"],
                                           half_extents=container["half_extents"],
                                           rotation=container["rotation"])
                    elif shape == TriggerColliderShape.cylinder:
                        obj = CylinderContainer(tag=tag,
                                                position=container["position"],
                                                radius=container["radius"],
                                                height=container["height"],
                                                rotation=container["rotation"])
                    elif shape == TriggerColliderShape.sphere:
                        obj = SphereContainer(tag=tag,
                                              position=container["position"],
                                              radius=container["radius"])
                    else:
                        raise Exception(shape)
                    self.container_shapes.append(obj)
            self.affordance_points: List[Dict[str, float]] = list()
            if "affordance_points" in data:
                self.affordance_points = data["affordance_points"]


class MaterialRecord(_Record):
    """
    A record of a visual material asset bundle.
    """

    def __init__(self, data: Optional[dict] = None):
        super().__init__(data)

        if data is None:
            self.type: str = "Ceramic"
        else:
            self.type: str = data["type"]


class SceneRecord(_Record):
    """
    A record of a scene asset bundle.
    """

    def __init__(self, data: Optional[dict] = None):
        super().__init__(data)

        self.rooms: List[Room] = list()
        if data is None:
            self.description: str = ""
            self.hdri: bool = False
            self.location: str = ""
        else:
            self.description: str = data["description"]
            self.hdri: bool = data["hdri"]
            self.location: str = data["location"]
            for room_data in data["rooms"]:
                main_region = InteriorRegion(region_id=room_data["main_region"]["region_id"],
                                             center=tuple(room_data["main_region"]["center"]),
                                             bounds=tuple(room_data["main_region"]["bounds"]),
                                             non_continuous_walls=room_data["main_region"]["non_continuous_walls"],
                                             walls_with_windows=room_data["main_region"]["walls_with_windows"])
                alcoves = []
                for alcove_data in room_data["alcoves"]:
                    alcoves.append(InteriorRegion(region_id=alcove_data["region_id"],
                                                  center=tuple(alcove_data["center"]),
                                                  bounds=tuple(alcove_data["bounds"]),
                                                  non_continuous_walls=alcove_data["non_continuous_walls"],
                                                  walls_with_windows=alcove_data["walls_with_windows"]))
                self.rooms.append(Room(main_region=main_region, alcoves=alcoves))


class HDRISkyboxRecord(_Record):
    """
    A record of an HDRI skybox asset bundle.
    """

    def __init__(self, data: Optional[dict] = None):
        super().__init__(data)

        if data is None:
            self.color_temperature: float = 0
            self.sun_elevation: float = 0
            self.sun_initial_angle: float = 0
            self.sun_intensity: float = 0
            self.initial_skybox_rotation: float = 0
            self.exposure: float = 0
            self.location: str = ""
        else:
            self.color_temperature: float = data["color_temperature"]
            self.sun_elevation: float = data["sun_elevation"]
            self.sun_initial_angle: float = data["sun_initial_angle"]
            self.sun_intensity: float = data["sun_intensity"]
            self.initial_skybox_rotation: float = data["initial_skybox_rotation"]
            self.exposure: float = data["exposure"]
            self.location: str = data["location"]


class HumanoidAnimationRecord(_Record):
    """
    A record for a humanoid animation asset bundle.
    """

    def __init__(self, data: Optional[dict] = None):
        super().__init__(data)

        if data is None:
            self.duration: float = 0
            self.loop: bool = False
            self.framerate: int = 0
            self.walk: bool = False
        else:
            self.duration: float = data["duration"]
            self.loop: bool = data["loop"]
            self.framerate: int = data["framerate"]
            self.walk: bool = data["walk"]

    def get_num_frames(self) -> int:
        """
        Returns the number of frames, given the duration and framerate.
        """

        return int(self.duration * self.framerate)


class HumanoidRecord(_Record):
    """
    A record for a humanoid asset bundle.
    """

    def __init__(self, data: Optional[dict] = None):
        super().__init__(data)
        self.collision_avoidance_distance: float = data["collision_avoidance_distance"]
        self.collision_avoidance_half_extents: Dict[str, float] = data["collision_avoidance_half_extents"]


class DroneRecord(_Record):
    """
    A record for a drone asset bundle.
    """

    def __init__(self, data: Optional[dict] = None):
        super().__init__(data)


class VehicleRecord(_Record):
    """
    A record for a vehicle asset bundle.
    """

    def __init__(self, data: Optional[dict] = None):
        super().__init__(data)


class RobotRecord(_Record):
    """
    A record for a robot asset bundle.
    """

    def __init__(self, data: Optional[dict] = None):
        super().__init__(data)
        self.source: str = data["source"]
        self.immovable: bool = data["immovable"]
        self.targets: dict = data["targets"]
        self.ik: list = data["ik"]


class VisualEffectRecord(_Record):
    """
    A record for a non-physical visual effect asset bundle.
    """

    def __init__(self, data: Optional[dict] = None):
        super().__init__(data)
        self.audio: bool = data["audio"]


T = TypeVar("T", bound=_Record)


class _Librarian(Generic[T]):
    """
    Base abstract class for a metadata librarian.
    """

    def __init__(self, library: str = ""):
        """
        :param library: The absolute path to the library .json file. If empty, a default path in the tdw module will be used.
        """

        if library == "":
            self.library = pkg_resources.resource_filename(__name__, "metadata_libraries/" + self.get_default_library())
        else:
            module_path = pkg_resources.resource_filename(__name__, "metadata_libraries/" + library)
            if Path(module_path).exists():
                self.library = module_path
            else:
                self.library = library

        with open(self.library, "rt") as f:
            self.data = json.load(f)

        self.description = self.data["description"]

        self.records: List[T] = []
        for key in self.data["records"]:
            record = self._generate_record(self.data["records"][key])
            temp_urls = dict()
            # De-localize URLs
            for p in record.urls:
                # Set an absolute path.
                absolute = False
                for prefix in ["file:///", "http://", "https://"]:
                    if record.urls[p].startswith(prefix):
                        temp_urls[p] = record.urls[p]
                        absolute = True
                # De-localize a local path.
                if not absolute:
                    temp_urls[p] = f"file:///{str(Path(self.library).parent.joinpath(record.urls[p]).resolve())}"
                temp_urls[p] = temp_urls[p].replace("\\", "/")
            record.urls = temp_urls
            self.records.append(record)

    def get_default_library(self) -> str:
        """
        Returns the default library path (which is always the first in the list of `get_library_filenames()`)
        """

        return self.get_library_filenames()[0]

    @staticmethod
    def create_library(description: str, path: str) -> None:
        """
        Create a new library JSON file.

        :param path: The absolute filepath to the .json records database file.
        :param description: A brief description of the library.
        """

        path = Path(path)
        data = {"description": description,
                "records": {}}
        path.write_text(json.dumps(data), encoding="utf-8")
        print(f"Created new library: {path}")

    @staticmethod
    def get_library_filenames() -> List[str]:
        """
        Returns a list of the filenames of the libraries of this type in the tdw module.
        """

        raise Exception()

    def get_record(self, name: str) -> Optional[T]:
        """
        Returns a record with the specified name. If that record can't be found, returns None.

        :param name: The name of the record.
        """

        records = [r for r in self.records if r.name == name]

        if len(records) == 0:
            return None
        else:
            return records[0]

    def search_records(self, search: str) -> List[T]:
        """
        Returns a list of records whose names include the search keyword.

        :param search: The string to search for in the model name.
        """

        return [r for r in self.records if search in r.name]

    def add_or_update_record(self, record: T, overwrite: bool, write: bool = True, quiet: bool = True) -> bool:
        """
        Add a new record or update an existing record.

        :param record: The record.
        :param overwrite: If true, overwrite the record if it already exists.
        :param write: If true, write the library data to disk (overwriting the existing file).
        :param quiet: If true, silently correct the model name if need be.
        """

        # Valid the name of the record.
        name_ok, name, problems = self.get_valid_record_name(record.name, overwrite)
        record.name = name
        if not name_ok and not quiet:
            print(f"Renaming this record to {name} because:")
            for p in problems:
                print(f"\t{p}")

        added = False
        if len([r for r in self.records if r.name == record.name]) > 0:
            # If this record exists and we want to overwrite, update the record.
            if overwrite:
                records_list = [r for r in self.records if r.name != record.name]
                records_list.append(record)
                added = True
        # Add the record.
        else:
            self.records.append(record)
            added = True

        # Write to disk.
        if added:
            if record.name in self.data["records"]:
                self.data["records"][record.name] = record.get_serializable()
            else:
                self.data["records"].update({record.name: record.get_serializable()})
        if write:
            self.write()

        return added

    def remove_record(self, record: Union[str, T], write: bool = True) -> bool:
        """
        Remove a record. Returns true if the record was removed.

        :param record: The record or the name of the record.
        :param write: If true, write the library data to disk  (overwriting the existing file).
        """

        if isinstance(record, str):
            record_name = record
        else:
            record_name = record.name

        records_list = [r for r in self.records if r.name != record_name]
        removed = len(records_list) < len(self.records)
        if removed:
            del self.data["records"][record_name]
            self.records = records_list
        if write:
            self.write()

        return removed

    def write(self, pretty=True) -> None:
        """
        Write the data to disk.

        :param pretty: Pretty print.
        """

        with open(self.library, "wt") as f:
            if pretty:
                json.dump(self.data, f, sort_keys=True, indent=4, cls=_Encoder)
            else:
                json.dump(self.data, f, cls=_Encoder)

    def get_valid_record_name(self, name: str, overwrite: bool) -> Tuple[bool, str, List[str]]:
        """
        Generates a valid record name. Returns: true if the name is good as-is, the new name, and a list of problems with the old name.

        :param name: The name of a record we'd like to add.
        :param overwrite: If true, raise an exception if the record doesn't exist. Otherwise, overwrite. If False: If the record exists, suggest a new name.
        """

        record_names = [r.name for r in self.records]

        if overwrite and name not in record_names:
            return False, name, [f"Can't override a record named {name} because no such record exists!"]

        good_name = name[:]
        ok = True
        problems: List[str] = []
        good_name = good_name.replace(" ", "_")
        if good_name != name:
            ok = False
            problems.append("Name has spaces. They have been replaced with underscores.")
        good_name = good_name.lower()
        if good_name != name:
            ok = False
            problems.append("Name has uppercase letters. They are now all lowercase.")

        if not overwrite and good_name in record_names:
            ok = False
            while good_name in record_names:
                good_name = good_name + token_hex(2)
            problems.append(f"A record named {name} already exists, and we don't want to overwrite it.")
        return ok, good_name, problems

    def _generate_record(self, data: dict) -> T:
        """
        Generate a record of type T from JSON data.

        :param data: The record JSON data.
        """

        raise Exception("Not defined.")


class ModelLibrarian(_Librarian[ModelRecord]):
    """
    Librarian class for model metadata.
    """

    def get_model_wnids_and_wcategories(self) -> Dict[str, str]:
        """
        Returns a dictionary of all model wnids and categories.
        Key=wnid Value=category
        """

        wnids: Dict[str, str] = {}
        for model in self.records:
            if model.wnid in wnids:
                if wnids[model.wnid] != model.wcategory:
                    print(f"WARNING: Model {model.name} wcategory is {model.wcategory} (expected: {wnids[model.wnid]})")
            else:
                wnids.update({model.wnid: model.wcategory})
        return wnids

    def get_model_wnids(self) -> List[str]:
        """
        Returns a list of all unique wnids in the database, sorted numerically.
        """

        return sorted(set([r.wnid for r in self.records]))

    def get_all_models_in_wnid(self, wnid: str) -> List[ModelRecord]:
        """
        Returns a list of all models with the same wnid.

        :param wnid: The WordNet ID.
        """

        return [r for r in self.records if r.wnid == wnid]

    def get_flex_models(self) -> List[ModelRecord]:
        """
        Returns a list of all Flex-compatible models.
        """

        return [r for r in self.records if r.flex]

    @staticmethod
    def get_library_filenames() -> List[str]:
        return ["models_core.json", "models_full.json", "models_special.json", "models_flex.json"]

    def _generate_record(self, data: dict) -> T:
        return ModelRecord(data)


class MaterialLibrarian(_Librarian[MaterialRecord]):
    """
    Librarian class for material metadata.
    """

    def get_all_materials_of_type(self, material_type: str) -> List[MaterialRecord]:
        """
        Returns a list of all material records of a given type.

        :param material_type: The type of material.
        """

        return [r for r in self.records if r.type == material_type]

    def get_material_types(self) -> List[str]:
        """
        Returns a list of all types of materials, sorted alphabetically.
        """

        return sorted(set([r.type for r in self.records]))

    @staticmethod
    def get_library_filenames() -> List[str]:
        return ["materials_med.json", "materials_low.json", "materials_high.json"]

    def _generate_record(self, data: dict) -> T:
        return MaterialRecord(data)


class SceneLibrarian(_Librarian[SceneRecord]):
    """
    Librarian class for scene metadata.
    """

    @staticmethod
    def get_library_filenames() -> List[str]:
        return ["scenes.json"]

    def _generate_record(self, data: dict) -> T:
        return SceneRecord(data)


class HDRISkyboxLibrarian(_Librarian[HDRISkyboxRecord]):
    """
    Librarian class for HDRI skybox metadata.
    """

    @staticmethod
    def get_library_filenames() -> List[str]:
        return ["hdri_skyboxes.json"]

    def _generate_record(self, data: dict) -> T:
        return HDRISkyboxRecord(data)


class HumanoidAnimationLibrarian(_Librarian[HumanoidAnimationRecord]):
    """
    Librarian class for humanoid animation metadata.
    """

    @staticmethod
    def get_library_filenames() -> List[str]:
        return ["humanoid_animations.json", "smpl_animations.json"]

    def _generate_record(self, data: dict) -> T:
        return HumanoidAnimationRecord(data)


class HumanoidLibrarian(_Librarian[HumanoidRecord]):
    """
    Librarian class for humanoid metadata.
    """

    @staticmethod
    def get_library_filenames() -> List[str]:
        return ["humanoids.json", "smpl_humanoids.json", "replicants.json", "wheelchair_replicants.json"]

    def _generate_record(self, data: dict) -> T:
        return HumanoidRecord(data)


class DroneLibrarian(_Librarian[DroneRecord]):
    """
    Librarian class for drone metadata.
    """

    @staticmethod
    def get_library_filenames() -> List[str]:
        return ["drones.json"]

    def _generate_record(self, data: dict) -> T:
        return DroneRecord(data)


class VehicleLibrarian(_Librarian[VehicleRecord]):
    """
    Librarian class for vehicle metadata.
    """

    @staticmethod
    def get_library_filenames() -> List[str]:
        return ["vehicles.json"]

    def _generate_record(self, data: dict) -> T:
        return VehicleRecord(data)


class RobotLibrarian(_Librarian[RobotRecord]):
    """
    Librarian class for robot metadata.
    """

    @staticmethod
    def get_library_filenames() -> List[str]:
        return ["robots.json"]

    def _generate_record(self, data: dict) -> T:
        return RobotRecord(data)


class VisualEffectLibrarian(_Librarian[VisualEffectRecord]):
    """
    Librarian class for non-physical visual effects.
    """

    @staticmethod
    def get_library_filenames() -> List[str]:
        return ["visual_effects.json", "flood_effects.json"]

    def _generate_record(self, data: dict) -> T:
        return VisualEffectRecord(data)
