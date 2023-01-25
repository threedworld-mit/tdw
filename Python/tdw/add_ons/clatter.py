from copy import copy
from typing import List, Dict, Union
import numpy as np
from tdw.add_ons.add_on import AddOn
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, SegmentationColors, Bounds, StaticRigidbodies, StaticRobot, StaticOculusTouch
from tdw.physics_audio.impact_material import ImpactMaterial
from tdw.physics_audio.scrape_model import DEFAULT_SCRAPE_MODELS
from tdw.physics_audio.clatter_object import ClatterObject, DEFAULT_OBJECTS
from tdw.librarian import MaterialLibrarian, ModelRecord


class Clatter(AddOn):
    """
    (TODO)
    """

    # The visual material librarian used for scrape surfaces.
    __VISUAL_MATERIAL_LIBRARIAN: MaterialLibrarian = MaterialLibrarian("materials_high.json")

    def __init__(self, objects: Dict[int, ClatterObject] = None, random_seed: int = None,
                 adjust_audio_settings: bool = True, simulation_amp: float = 0.5,
                 min_collision_speed: float = 0.00001, area_new_collision: float = 1e-5, scrape_angle: float = 80,
                 impact_area_ratio: float = 5, roll_angular_speed: float = 0.5, max_contact_separation: float = 1e-8,
                 filter_duplicates: bool = True, max_num_contacts: int = 16, sound_timeout: float = 0.1,
                 prevent_impact_distortion: bool = True, clamp_impact_contact_time: bool = True,
                 min_time_between_impacts: float = 0.05, max_time_between_impacts: float = 3,
                 max_scrape_speed: float = 5, loop_scrape_audio: bool = True, default_object: ClatterObject = None,
                 environment: ClatterObject = None, robot_material: ImpactMaterial = ImpactMaterial.metal,
                 human_material: ImpactMaterial = ImpactMaterial.cardboard, resonance_audio: bool = False):
        """
        :param objects: A dictionary of [`ClatterObject`](../physics_audio/clatter_object.md) overrides. Key = object ID. If None, the list is empty. If an object is in the scene but not in this list, TDW will try to automatically create a `ClatterObject` for it, either using pre-calculated data or by deriving parameter values.
        :param random_seed: The random seed. If None, the seed is randomly selected within the build.
        :param adjust_audio_settings: If True, automatically adjust the global audio settings (framerate and DSP size) for the best playback quality.
        :param simulation_amp: The overall amplitude of the simulation. The amplitude of generated audio is scaled by this factor. Must be between 0 and 0.99
        :param min_collision_speed: The minimum collision speed in meters per second. If a collision has a speed less than this, it is ignored.
        :param area_new_collision: On a collision stay event, if the previous area is None and the current area is greater than this, the audio event is either an impact or a scrape; see scrapeAngle. 
        :param scrape_angle: On a collision stay event, there is a large new contact area (see area_new_collision), if the angle between Vector3.up and the normalized relative velocity of the collision is greater than this value, then the audio event is a scrape. Otherwise, it's an impact.
        :param impact_area_ratio: On a collision stay event, if the area of the collision increases by at least this factor, the audio event is an impact.
        :param roll_angular_speed: On a collision stay event, if the angular speed is this or greater, the audio event is a roll; otherwise, it's a scrape.
        :param max_contact_separation: On a collision stay event, if we think the collision is an impact but any of the contact points are this far away or greater, the audio event is none.
        :param filter_duplicates: Each ClatterObject tries to filter duplicate collision events in two ways. First, it will remove any reciprocal pairs of objects, i.e. it will accept a collision between objects 0 and 1 but not objects 1 and 0. Second, it will register only the first collision between objects per main-thread update (multiple collisions can be registered because there are many physics fixed update calls in between). To allow duplicate events, set this field to False.
        :param max_num_contacts: The maximum number of contact points that will be evaluated when setting the contact area and speed. A higher number can mean somewhat greater precision but at the cost of performance.
        :param sound_timeout: Timeout and destroy a Sound if it hasn't received new samples data after this many seconds.
        :param prevent_impact_distortion: If True, clamp impact audio amplitude values to less than or equal to 0.99, preventing distortion.
        :param clamp_impact_contact_time: If True, clamp impact contact time values to a plausible value. Set this to False if you want to generate impacts with unusually long contact times.
        :param min_time_between_impacts: The minimum time in seconds between impacts. If an impact occurs an this much time hasn't yet elapsed, the impact will be ignored. This can prevent strange "droning" sounds caused by too many impacts in rapid succession.
        :param max_time_between_impacts: The maximum time in seconds between impacts. After this many seconds, this impact series will end and a subsequent impact collision will start a new Impact.
        :param max_scrape_speed: For the purposes of scrape audio generation, the collision speed is clamped to this maximum value.
        :param loop_scrape_audio: If True, fill in silences while scrape audio is being generated by continuously looping the current chunk of scrape audio until either there is new scrape audio or the scrape event ends.
        :param default_object: The [`ClatterObject`](../physics_audio/clatter_object.md) values used when none can be found or derived. If None, defaults to: `ClatterObject(AudioMaterial.plastic_hard, 1, 0.2, 0.45, None)`.
        :param environment: The [`ClatterObject`](../physics_audio/clatter_object.md) used for the environment (floors, walls, etc.). If None, defaults to: `ClatterObject(AudioMaterial.wood_medium, 4, 0.5, 0.1, 100)`.
        :param robot_material: The [`ImpactMaterial`](../physics_audio/impact_material.md) used for robots.
        :param human_material: The [`ImpactMaterial`](../physics_audio/impact_material.md) used for human body parts in VR.
        :param resonance_audio: If True, use [Resonance Audio](../../lessons/audio/resonance_audio.md) to play audio.
        """

        super().__init__()
        if objects is None:
            """:field
            A dictionary of [`ClatterObject`](../physics_audio/clatter_object.md) overrides. Key = object ID. If an object is in the scene but not in this list, TDW will try to automatically create a `ClatterObject` for it, either using pre-calculated data or by deriving parameter values.
            """
            self.objects: Dict[int, ClatterObject] = dict()
        else:
            self.objects = objects
        if random_seed is None:
            """:field
            The random seed. If None, the seed is randomly selected within the build.
            """
            self.random_seed: int = -1
            self._generate_random_seed: bool = True
        else:
            self.random_seed = random_seed
            self._generate_random_seed = False
        """:field
        If True, automatically adjust the global audio settings (framerate and DSP size) for the best playback quality.
        """
        self.adjust_audio_settings: bool = adjust_audio_settings
        """:field
        The overall amplitude of the simulation. The amplitude of generated audio is scaled by this factor. Must be between 0 and 0.99
        """
        self.simulation_amp: float = simulation_amp
        """:field
        The minimum collision speed in meters per second. If a `CollisionEvent` has a speed less than this, it is ignored.
        """
        self.min_collision_speed: float = min_collision_speed
        """:field
        On a collision stay event, if the previous area is None and the current area is greater than this, the audio event is either an impact or a scrape; see scrapeAngle. 
        """
        self.area_new_collision: float = area_new_collision
        """:field
        On a collision stay event, there is a large new contact area (see areaNewCollision), if the angle between Vector3.up and the normalized relative velocity of the collision is greater than this value, then the audio event is a scrape. Otherwise, it's an impact. 
        """
        self.scrape_angle: float = scrape_angle
        """:field
        On a collision stay event, if the area of the collision increases by at least this factor, the audio event is an impact.
        """
        self.impact_area_ratio: float = impact_area_ratio
        """:field
        On a collision stay event, if the angular speed is this or greater, the audio event is a roll; otherwise, it's a scrape.
        """
        self.roll_angular_speed: float = roll_angular_speed
        """:field
        On a collision stay event, if we think the collision is an impact but any of the contact points are this far away or greater, the audio event is none.
        """
        self.max_contact_separation: float = max_contact_separation
        """:field
        Each ClatterObject tries to filter duplicate collision events in two ways. First, it will remove any reciprocal pairs of objects, i.e. it will accept a collision between objects 0 and 1 but not objects 1 and 0. Second, it will register only the first collision between objects per main-thread update (multiple collisions can be registered because there are many physics fixed update calls in between). To allow duplicate events, set this field to False.
        """
        self.filter_duplicates: bool = filter_duplicates
        """:field
        The maximum number of contact points that will be evaluated when setting the contact area and speed. A higher number can mean somewhat greater precision but at the cost of performance.
        """
        self.max_num_contacts: int = max_num_contacts
        """:field
        Timeout and destroy a Sound if it hasn't received new samples data after this many seconds.
        """
        self.sound_timeout: float = sound_timeout
        """:field
        If True, clamp impact audio amplitude values to less than or equal to 0.99, preventing distortion.
        """
        self.prevent_impact_distortion: bool = prevent_impact_distortion
        """:field
        If True, clamp impact contact time values to a plausible value. Set this to False if you want to generate impacts with unusually long contact times.
        """
        self.clamp_impact_contact_time: bool = clamp_impact_contact_time
        """:field
        The minimum time in seconds between impacts. If an impact occurs an this much time hasn't yet elapsed, the impact will be ignored. This can prevent strange "droning" sounds caused by too many impacts in rapid succession.
        """
        self.min_time_between_impacts: float = min_time_between_impacts
        """:field
        The maximum time in seconds between impacts. After this many seconds, this impact series will end and a subsequent impact collision will start a new Impact.
        """
        self.max_time_between_impacts: float = max_time_between_impacts
        """:field
        For the purposes of scrape audio generation, the collision speed is clamped to this maximum value.
        """
        self.max_scrape_speed: float = max_scrape_speed
        """:field
        If True, fill in silences while scrape audio is being generated by continuously looping the current chunk of scrape audio until either there is new scrape audio or the scrape event ends.
        """
        self.loop_scrape_audio: bool = loop_scrape_audio
        if default_object is None:
            """:field
            The [`ClatterObject`](../physics_audio/clatter_object.md) values used when none can be found or derived.
            """
            self.default_object: ClatterObject = Clatter._get_default_clatter_object()
        else:
            self.default_object = default_object
        if environment is None:
            """:field
            The [`ClatterObject`](../physics_audio/clatter_object.md) used for the environment (floors, walls, etc.).
            """
            self.environment: ClatterObject = Clatter._get_default_environment_clatter_object()
        else:
            self.environment = environment
        """:field
        The [`AudioMaterial`](../physics_audio/impact_material.md) used for robot joints.
        """
        self.robot_material: ImpactMaterial = robot_material
        """:field
        The [`AudioMaterial`](../physics_audio/impact_material.md) used for human body parts in VR.
        """
        self.human_material: ImpactMaterial = human_material
        """:field
        If True, use Resonance Audio to play audio.
        """
        self.resonance_audio: bool = resonance_audio
        self._initialized_clatter: bool = False

    def get_initialization_commands(self) -> List[dict]:
        return [{"$type": "send_segmentation_colors"},
                {"$type": "send_bounds"},
                {"$type": "send_static_rigidbodies"},
                {"$type": "send_static_robots"},
                {"$type": "send_static_oculus_touch"}]

    def on_send(self, resp: List[bytes]) -> None:
        if not self._initialized_clatter:
            self._initialized_clatter = True
            # Initialize each object.
            categories: Dict[int, str] = dict()
            names: Dict[int, str] = dict()
            robot_joints: Dict[int, dict] = dict()
            object_masses: Dict[int, float] = dict()
            extents: Dict[int, np.ndarray] = dict()
            vr_nodes: Dict[int, ClatterObject] = dict()
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                if r_id == "boun":
                    boun = Bounds(resp[i])
                    for j in range(boun.get_num()):
                        extents[boun.get_id(j)] = TDWUtils.get_bounds_extents(bounds=boun, index=j)
                if r_id == "segm":
                    segm = SegmentationColors(resp[i])
                    for j in range(segm.get_num()):
                        object_id = segm.get_object_id(j)
                        model_name = segm.get_object_name(j).lower()
                        names[object_id] = model_name
                        categories[object_id] = segm.get_object_category(j)
                        # Enable a scrape surface.
                        if model_name in DEFAULT_SCRAPE_MODELS or (object_id in self.objects and self.objects[object_id].scrape_model is not None):
                            scrape_model = self.objects[object_id].scrape_model
                            # Add the visual material.
                            material_record = Clatter.__VISUAL_MATERIAL_LIBRARIAN.get_record(name=scrape_model.visual_material)
                            self.commands.append({"$type": "add_material",
                                                  "name": material_record.name,
                                                  "url": material_record.get_url()})
                            # Set the visual material.
                            for sub_object in scrape_model.sub_objects:
                                self.commands.append({"$type": "set_visual_material",
                                                      "material_index": sub_object.material_index,
                                                      "material_name": material_record.name,
                                                      "object_name": sub_object.name,
                                                      "id": object_id})
                elif r_id == "srob":
                    srob = StaticRobot(resp[i])
                    for j in range(srob.get_num_joints()):
                        joint_id = srob.get_joint_id(j)
                        robot_joints[joint_id] = {"name": srob.get_joint_name(j),
                                                  "mass": srob.get_joint_mass(j)}
                elif r_id == "srig":
                    srig = StaticRigidbodies(resp[i])
                    for j in range(srig.get_num()):
                        object_masses[srig.get_id(j)] = srig.get_mass(j)
                # Add VR nodes.
                elif r_id == "soct":
                    soct = StaticOculusTouch(resp[i])
                    if soct.get_human_hands():
                        vr_material = self.human_material
                    else:
                        vr_material = self.robot_material
                    for vr_node_id in [soct.get_body_id(), soct.get_left_hand_id(), soct.get_right_hand_id()]:
                        vr_nodes[vr_node_id] = ClatterObject(impact_material=vr_material,
                                                             size=self.default_object.size,
                                                             amp=self.default_object.amp,
                                                             resonance=self.default_object.resonance)
            need_to_derive: List[int] = list()
            for object_id in names:
                name = names[object_id]
                # Use override data.
                if object_id in self.objects:
                    pass
                # Use default audio data.
                elif name in DEFAULT_OBJECTS:
                    self.objects[object_id] = copy(DEFAULT_OBJECTS[name])
                else:
                    need_to_derive.append(object_id)
            current_values = self.objects.values()
            derived_data: Dict[int, ClatterObject] = dict()
            for object_id in need_to_derive:
                # Fallback option: comparable objects in the same category.
                objects_in_same_category = [o for o in categories if categories[o] == categories[object_id]]
                if len(objects_in_same_category) > 0:
                    amps: List[float] = [a.amp for a in current_values]
                    materials: List[ImpactMaterial] = [a.impact_material for a in current_values]
                    resonances: List[float] = [a.resonance for a in current_values]
                # Fallback option: Find objects with similar volume.
                else:
                    amps: List[float] = list()
                    materials: List[ImpactMaterial] = list()
                    resonances: List[float] = list()
                    for m_id in object_masses:
                        if m_id == object_id or m_id not in self.objects:
                            continue
                        if np.abs(object_masses[m_id] / object_masses[object_id]) < 1.5:
                            amps.append(self.objects[m_id].amp)
                            materials.append(self.objects[m_id].impact_material)
                            resonances.append(self.objects[m_id].resonance)
                # Fallback option: Use default values.
                if len(amps) == 0:
                    amp: float = self.default_object.amp
                    material: ImpactMaterial = self.default_object.impact_material
                    resonance: float = self.default_object.resonance
                # Get averages or maximums of each value.
                else:
                    amp: float = round(sum(amps) / len(amps), 3)
                    material: ImpactMaterial = max(set(materials), key=materials.count)
                    resonance: float = round(sum(resonances) / len(resonances), 3)
                derived_data[object_id] = ClatterObject(impact_material=material,
                                                        size=Clatter.get_size(model=extents[object_id]),
                                                        amp=amp,
                                                        resonance=resonance)
            # Add the derived data.
            for object_id in derived_data:
                self.objects[object_id] = derived_data[object_id]
            # Add robot joints.
            for joint_id in robot_joints:
                self.objects[joint_id] = ClatterObject(impact_material=self.robot_material,
                                                       size=self.default_object.size,
                                                       amp=self.default_object.amp,
                                                       resonance=self.default_object.resonance)
            # Add VR nodes.
            for vr_node_id in vr_nodes:
                self.objects[vr_node_id] = vr_nodes[vr_node_id]
            # Clatterize.
            for object_id in self.objects:
                clatter_object: ClatterObject = self.objects[object_id]
                has_scrape_material = clatter_object.scrape_model is not None
                clatterize_command = {"$type": "clatterize_object",
                                      "id": int(object_id),
                                      "impact_material": clatter_object.impact_material.name,
                                      "size": int(clatter_object.size),
                                      "amp": float(clatter_object.amp),
                                      "resonance": float(clatter_object.resonance),
                                      "has_scrape_material": has_scrape_material}
                if has_scrape_material:
                    clatterize_command["scrape_material"] = clatter_object.scrape_model.scrape_material
                if clatter_object.fake_mass is not None:
                    clatterize_command["has_fake_mass"] = True
                    clatterize_command["fake_mass"] = float(clatter_object.fake_mass)
                self.commands.append(clatterize_command)
            # Initialize Clatter.
            self.commands.append({"$type": "initialize_clatter",
                                  "generate_random_seed": self._generate_random_seed,
                                  "random_seed": self.random_seed,
                                  "adjust_audio_settings": self.adjust_audio_settings,
                                  "simulation_amp": self.simulation_amp,
                                  "min_collision_speed": self.min_collision_speed,
                                  "area_new_collision": self.area_new_collision,
                                  "scrape_angle": self.scrape_angle,
                                  "impact_area_ratio": self.impact_area_ratio,
                                  "roll_angular_speed": self.roll_angular_speed,
                                  "max_contact_separation": self.max_contact_separation,
                                  "filter_duplicates": self.filter_duplicates,
                                  "max_num_contacts": self.max_num_contacts,
                                  "sound_timeout": self.sound_timeout,
                                  "prevent_impact_distortion": self.prevent_impact_distortion,
                                  "clamp_impact_contact_time": self.clamp_impact_contact_time,
                                  "min_time_between_impacts": self.min_time_between_impacts,
                                  "max_time_between_impacts": self.max_time_between_impacts,
                                  "max_scrape_speed": self.max_scrape_speed,
                                  "loop_scrape_audio": self.loop_scrape_audio,
                                  "environment_impact_material": self.environment.impact_material.name,
                                  "environment_size": self.environment.size,
                                  "environment_amp": self.environment.amp,
                                  "environment_resonance": self.environment.resonance,
                                  "environment_mass": self.environment.fake_mass,
                                  "resonance_audio": self.resonance_audio})

    def reset(self, objects: Dict[int, ClatterObject] = None, random_seed: int = None,
              adjust_audio_settings: bool = True, simulation_amp: float = 0.5, min_collision_speed: float = 0.00001,
              area_new_collision: float = 1e-5, scrape_angle: float = 80, impact_area_ratio: float = 5,
              roll_angular_speed: float = 0.5, max_contact_separation: float = 1e-8, filter_duplicates: bool = True,
              max_num_contacts: int = 16, sound_timeout: float = 0.1, prevent_impact_distortion: bool = True,
              clamp_impact_contact_time: bool = True, min_time_between_impacts: float = 0.05,
              max_time_between_impacts: float = 3, max_scrape_speed: float = 5, loop_scrape_audio: bool = True,
              default_object: ClatterObject = None, environment: ClatterObject = None, 
              robot_material: ImpactMaterial = ImpactMaterial.metal, 
              human_material: ImpactMaterial = ImpactMaterial.cardboard, resonance_audio: bool = False):
        """
        Reset Clatter.

        :param objects: A dictionary of [`ClatterObject`](../physics_audio/clatter_object.md) overrides. Key = object ID. If None, the list is empty. If an object is in the scene but not in this list, TDW will try to automatically create a `ClatterObject` for it, either using pre-calculated data or by deriving parameter values.
        :param random_seed: The random seed. If None, the seed is randomly selected within the build.
        :param adjust_audio_settings: If True, automatically adjust the global audio settings (framerate and DSP size) for the best playback quality.
        :param simulation_amp: The overall amplitude of the simulation. The amplitude of generated audio is scaled by this factor. Must be between 0 and 0.99
        :param min_collision_speed: The minimum collision speed in meters per second. If a collision has a speed less than this, it is ignored.
        :param area_new_collision: On a collision stay event, if the previous area is None and the current area is greater than this, the audio event is either an impact or a scrape; see scrapeAngle.
        :param scrape_angle: On a collision stay event, there is a large new contact area (see area_new_collision), if the angle between Vector3.up and the normalized relative velocity of the collision is greater than this value, then the audio event is a scrape. Otherwise, it's an impact.
        :param impact_area_ratio: On a collision stay event, if the area of the collision increases by at least this factor, the audio event is an impact.
        :param roll_angular_speed: On a collision stay event, if the angular speed is this or greater, the audio event is a roll; otherwise, it's a scrape.
        :param max_contact_separation: On a collision stay event, if we think the collision is an impact but any of the contact points are this far away or greater, the audio event is none.
        :param filter_duplicates: Each ClatterObject tries to filter duplicate collision events in two ways. First, it will remove any reciprocal pairs of objects, i.e. it will accept a collision between objects 0 and 1 but not objects 1 and 0. Second, it will register only the first collision between objects per main-thread update (multiple collisions can be registered because there are many physics fixed update calls in between). To allow duplicate events, set this field to False.
        :param max_num_contacts: The maximum number of contact points that will be evaluated when setting the contact area and speed. A higher number can mean somewhat greater precision but at the cost of performance.
        :param sound_timeout: Timeout and destroy a Sound if it hasn't received new samples data after this many seconds.
        :param prevent_impact_distortion: If True, clamp impact audio amplitude values to less than or equal to 0.99, preventing distortion.
        :param clamp_impact_contact_time: If True, clamp impact contact time values to a plausible value. Set this to False if you want to generate impacts with unusually long contact times.
        :param min_time_between_impacts: The minimum time in seconds between impacts. If an impact occurs an this much time hasn't yet elapsed, the impact will be ignored. This can prevent strange "droning" sounds caused by too many impacts in rapid succession.
        :param max_time_between_impacts: The maximum time in seconds between impacts. After this many seconds, this impact series will end and a subsequent impact collision will start a new Impact.
        :param max_scrape_speed: For the purposes of scrape audio generation, the collision speed is clamped to this maximum value.
        :param loop_scrape_audio: If True, fill in silences while scrape audio is being generated by continuously looping the current chunk of scrape audio until either there is new scrape audio or the scrape event ends.
        :param default_object: The [`ClatterObject`](../physics_audio/clatter_object.md) values used when none can be found or derived. If None, defaults to: `ClatterObject(AudioMaterial.plastic_hard, 1, 0.2, 0.45, None)`.
        :param environment: The [`ClatterObject`](../physics_audio/clatter_object.md) used for the environment (floors, walls, etc.). If None, defaults to: `ClatterObject(AudioMaterial.wood_medium, 4, 0.5, 0.1, 100)`.
        :param robot_material: The [`ImpactMaterial`](../physics_audio/impact_material.md) used for robot joints.
        :param human_material: The [`ImpactMaterial`](../physics_audio/impact_material.md) used for human body parts in VR.
        :param resonance_audio: If True, use [Resonance Audio](../../lessons/audio/resonance_audio.md) to play audio.
        """

        self.initialized = False
        self.objects.clear()
        if objects is not None:
            self.objects.update(objects)
        if random_seed is None:
            self.random_seed = -1
            self._generate_random_seed = True
        else:
            self.random_seed = random_seed
            self._generate_random_seed = False
        self.adjust_audio_settings = adjust_audio_settings
        self.simulation_amp = simulation_amp
        self.min_collision_speed = min_collision_speed
        self.area_new_collision = area_new_collision
        self.scrape_angle = scrape_angle
        self.impact_area_ratio = impact_area_ratio
        self.roll_angular_speed = roll_angular_speed
        self.max_contact_separation = max_contact_separation
        self.filter_duplicates = filter_duplicates
        self.max_num_contacts = max_num_contacts
        self.sound_timeout = sound_timeout
        self.prevent_impact_distortion = prevent_impact_distortion
        self.clamp_impact_contact_time = clamp_impact_contact_time
        self.min_time_between_impacts = min_time_between_impacts
        self.max_time_between_impacts = max_time_between_impacts
        self.max_scrape_speed = max_scrape_speed
        self.loop_scrape_audio = loop_scrape_audio
        if default_object is None:
            self.default_object = Clatter._get_default_clatter_object()
        else:
            self.default_object = default_object
        if environment is None:
            self.environment = Clatter._get_default_environment_clatter_object()
        else:
            self.environment = environment
        self.robot_material = robot_material
        self.human_material = human_material
        self.resonance_audio = resonance_audio
        self._initialized_clatter = False

    @staticmethod
    def get_size(model: Union[np.ndarray, ModelRecord]) -> int:
        """
        :param model: Either the extents of an object or a model record.

        :return: The `size` integer of the object.
        """

        if isinstance(model, np.ndarray):
            s = sum(model)
        elif isinstance(model, ModelRecord):
            s = sum(TDWUtils.get_bounds_extents(bounds=model.bounds))
        else:
            raise Exception(f"Invalid extents: {model}")
        if s <= 0.1:
            return 0
        elif s <= 0.02:
            return 1
        elif s <= 0.5:
            return 2
        elif s <= 1:
            return 3
        elif s <= 3:
            return 4
        else:
            return 5

    @staticmethod
    def _get_default_clatter_object() -> ClatterObject:
        """
        :return: The default ClatterObject.
        """
        
        return ClatterObject(impact_material=ImpactMaterial.plastic_hard,
                             size=1,
                             amp=0.2,
                             resonance=0.45)

    @staticmethod
    def _get_default_environment_clatter_object() -> ClatterObject:
        """
        :return: The default environment ClatterObject.
        """

        return ClatterObject(impact_material=ImpactMaterial.wood_medium,
                             size=4,
                             amp=0.5,
                             resonance=0.1,
                             fake_mass=100)
