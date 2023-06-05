from time import time
from os import urandom
import base64
import math
import json
from pathlib import Path
from pkg_resources import resource_filename
from typing import Dict, Optional, Union, List, Tuple
import numpy as np
import scipy.signal as sg
from scipy.ndimage import gaussian_filter1d, uniform_filter1d
from pydub import AudioSegment
from tdw.tdw_utils import TDWUtils
from tdw.librarian import ModelRecord
from tdw.output_data import OutputData, Rigidbodies, StaticRobot, SegmentationColors, StaticRigidbodies, \
    RobotJointVelocities, StaticOculusTouch, AudioSourceDone, Bounds
from tdw.physics_audio.audio_material import AudioMaterial
from tdw.physics_audio.object_audio_static import ObjectAudioStatic, DEFAULT_OBJECT_AUDIO_STATIC_DATA
from tdw.physics_audio.modes import Modes
from tdw.physics_audio.base64_sound import Base64Sound
from tdw.physics_audio.collision_audio_info import CollisionAudioInfo
from tdw.physics_audio.collision_audio_type import CollisionAudioType
from tdw.physics_audio.collision_audio_event import CollisionAudioEvent
from tdw.physics_audio.scrape_model import ScrapeModel, DEFAULT_SCRAPE_MODELS
from tdw.physics_audio.scrape_material import ScrapeMaterial
from tdw.object_data.rigidbody import Rigidbody
from tdw.audio_constants import SAMPLE_RATE, CHANNELS, SAMPLE_WIDTH
from tdw.add_ons.collision_manager import CollisionManager
from tdw.librarian import MaterialLibrarian


class PyImpact(CollisionManager):
    """
    **PyImpact has been deprecated. Use [`Clatter`](clatter.md) instead.**

    Generate impact sounds from physics data. Sounds can be synthesized automatically (for general use-cases) or manually (for advanced use-cases).

    ```python
    from tdw.controller import Controller
    from tdw.tdw_utils import TDWUtils
    from tdw.add_ons.audio_initializer import AudioInitializer
    from tdw.add_ons.py_impact import PyImpact

    c = Controller()
    commands = [TDWUtils.create_empty_room(12, 12)]
    commands.extend(TDWUtils.create_avatar(avatar_id="a",
                                           position={"x": 1, "y": 1.6, "z": -2},
                                           look_at={"x": 0, "y": 0.5, "z": 0}))
    commands.extend(c.get_add_physics_object(model_name="vase_02",
                                             position={"x": 0, "y": 3, "z": 0},
                                             object_id=c.get_unique_id()))
    audio_initializer = AudioInitializer(avatar_id="a")
    py_impact = PyImpact()
    c.add_ons.extend([audio_initializer, py_impact])
    c.communicate(commands)
    for i in range(200):
        c.communicate([])
    c.communicate({"$type": "terminate"})
    ```

    When using PyImpact, please cite  [Traer,Cusimano and McDermott, A perceptually inspired generative model of rigid-body contact sounds, Digital Audio Effects, (DAFx), 2019](http://dafx2019.bcu.ac.uk/papers/DAFx2019_paper_57.pdf) and [Agarwal, Cusimano, Traer, and McDermott, Object-based synthesis of scraping and rolling sounds based on non-linear physical constraints, (DAFx), 2021](http://mcdermottlab.mit.edu/bib2php/pubs/makeAbs.php?loc=agarwal21).

    ```
    @article {4500,
        title = {A perceptually inspired generative model of rigid-body contact sounds},
        journal = {Proceedings of the 22nd International Conference on Digital Audio Effects (DAFx-19)},
        year = {2019},
        month = {09/2019},
        abstract = {<p>Contact between rigid-body objects produces a diversity of impact and friction sounds. These sounds can be synthesized with detailed simulations of the motion, vibration and sound radiation of the objects, but such synthesis is computationally expensive and prohibitively slow for many applications. Moreover, detailed physical simulations may not be necessary for perceptually compelling synthesis; humans infer ecologically relevant causes of sound, such as material categories, but not with arbitrary precision. We present a generative model of impact sounds which summarizes the effect of physical variables on acoustic features via statistical distributions fit to empirical measurements of object acoustics. Perceptual experiments show that sampling from these distributions allows efficient synthesis of realistic impact and scraping sounds that convey material, mass, and motion.</p>
    },
        author = {James Traer and Maddie Cusimano and Josh H. McDermott}
    }
    ```

    ```
    @inproceedings{agarwal21,
         TITLE= "Object-based synthesis of scraping and rolling sounds based on non-linear physical constraints",
         AUTHOR= "V Agarwal and M Cusimano and J Traer and J H McDermott",
         booktitle= "The 24th International Conference on Digital Audio Effects (DAFx-21)",
         MONTH= "September",
         YEAR= 2021,
         PDF-URL= "http://mcdermottlab.mit.edu/papers/Agarwal_etal_2021_scraping_rolling_synthesis_DAFx.pdf",
    }
    ```
    """

    """:class_var
    100ms of silence. Used for scrapes.
    """
    SILENCE_100MS: AudioSegment = AudioSegment.silent(duration=100, frame_rate=SAMPLE_RATE)
    """:class_var
    The maximum velocity allowed for a scrape.
    """
    SCRAPE_MAX_VELOCITY: float = 1
    """:class_var
    Meters per pixel on the scrape surface.
    """
    SCRAPE_M_PER_PIXEL: float = 1394.068 * 10 ** -9
    """:class_var
    The default amp value for objects.
    """
    DEFAULT_AMP: float = 0.2
    """:class_var
    The default [material](../physics_audio/audio_material.md) for objects.
    """
    DEFAULT_MATERIAL: AudioMaterial = AudioMaterial.plastic_hard
    """:class_var
    The default resonance value for objects.
    """
    DEFAULT_RESONANCE: float = 0.45
    """:class_var
    The default audio size "bucket" for objects.
    """
    DEFAULT_SIZE: int = 1
    """:class_var
    The assumed bounciness value for robot joints.
    """
    ROBOT_JOINT_BOUNCINESS: float = 0.6
    """:class_var
    The [material](../physics_audio/audio_material.md) used for robot joints.
    """
    ROBOT_JOINT_MATERIAL: AudioMaterial = AudioMaterial.metal
    """:class_var
    The [material](../physics_audio/audio_material.md) used for human body parts in VR.
    """
    VR_HUMAN_MATERIAL: AudioMaterial = AudioMaterial.cardboard
    """:class_var
    The assumed bounciness value for human body parts such as in VR.
    """
    VR_HUMAN_BOUNCINESS: float = 0.3
    """:class_var
    The amp value for the floor.
    """
    FLOOR_AMP: float = 0.5
    """:class_var
    The size "bucket" for the floor.
    """
    FLOOR_SIZE: int = 4
    """:class_var
    The mass of the floor.
    """
    FLOOR_MASS: int = 100
    # Visual material librarian used for scrape surfaces.
    __VISUAL_MATERIAL_LIBRARIAN: MaterialLibrarian = MaterialLibrarian("materials_high.json")

    def __init__(self, initial_amp: float = 0.5, prevent_distortion: bool = True, logging: bool = False,
                 static_audio_data_overrides: Dict[int, ObjectAudioStatic] = None,
                 resonance_audio: bool = False, floor: AudioMaterial = AudioMaterial.wood_medium,
                 rng: np.random.RandomState = None, auto: bool = True, scrape: bool = True,
                 scrape_objects: Dict[int, ScrapeModel] = None, min_time_between_impact_events: float = 0.25):
        """
        :param initial_amp: The initial amplitude, i.e. the "master volume". Must be > 0 and < 1.
        :param prevent_distortion: If True, clamp amp values to <= 0.99
        :param logging: If True, log mode properties for all colliding objects, as json.
        :param static_audio_data_overrides: If not None, a dictionary of audio data. Key = Object ID; Value = [`ObjectAudioStatic`](../physics_audio/object_audio_static.md). These audio values will be applied to these objects instead of default values.
        :param resonance_audio: If True, the simulation is using Resonance Audio.
        :param floor: The floor material.
        :param rng: The random number generator. If None, a random number generator with a random seed is created.
        :param auto: If True, PyImpact will evaluate the simulation state per `communicate()` call and automatically generate audio.
        :param scrape: If True, initialize certain objects as scrape surfaces: Change their visual material(s) and enable them for scrape audio. See: `tdw.physics_audio.scrape_model.DEFAULT_SCRAPE_MODELS`
        :param scrape_objects: If `scrape == True` and this is not None, this dictionary can be used to manually set scrape surfaces. Key = Object ID. Value = [`ScrapeModel`](../physics_audio/scrape_model.md).
        :param min_time_between_impact_events: The minimum time in seconds between two impact events that involve the same primary object.
        """

        super().__init__()

        if rng is None:
            """:field
            The random number generator.
            """
            self.rng: np.random.RandomState = np.random.RandomState()
        else:
            self.rng = rng

        assert 0 < initial_amp < 1, f"initial_amp is {initial_amp} (must be > 0 and < 1)."

        """:field
        The initial amplitude, i.e. the "master volume". Must be > 0 and < 1.
        """
        self.initial_amp = initial_amp
        """:field
        If True, clamp amp values to <= 0.99
        """
        self.prevent_distortion = prevent_distortion
        """:field
        If True, log mode properties for all colliding objects, as json.
        """
        self.logging = logging

        """:field
        The collision info per set of objects.
        """
        self.object_modes: Dict[int, Dict[int, CollisionAudioInfo]] = dict()
        """:field
        If True, the simulation is using Resonance Audio.
        """
        self.resonance_audio: bool = resonance_audio
        """:field
        The floor material.
        """
        self.floor: AudioMaterial = floor

        """:field
        Cached material data.
        """
        self.material_data: Dict[str, dict] = {}
        material_list = ["ceramic", "wood_hard", "wood_medium", "wood_soft", "metal", "glass", "paper", "cardboard",
                         "leather", "fabric", "plastic_hard", "plastic_soft_foam", "rubber", "stone"]
        for mat in material_list:
            for i in range(6):
                # Load the JSON data.
                mat_name = mat + "_" + str(i)
                path = mat_name + "_mm"
                data = json.loads(Path(resource_filename(__name__, f"py_impact/material_data/{path}.json")).read_text())
                self.material_data.update({mat_name: data})
        """:field
        Cached scrape surface data.
        """
        self.scrape_surface_data: Dict[ScrapeMaterial, Dict[str, np.ndarray]] = {}
        """:field
        A dictionary of all [scrape models](../physics_audio/scrape_model.md) in the scene. If `scrape == False`, this dictionary is empty. Key = Object ID.
        """
        self._scrape_objects: Dict[int, ScrapeModel] = dict()
        self._scrape: bool = scrape
        # Use scrape surfaces.
        if self._scrape and scrape_objects is not None:
            for k in scrape_objects:
                self._scrape_objects[k] = scrape_objects[k]
        """:field
        The mode properties log.
        """
        self.mode_properties_log = dict()
        """:field
        If True, PyImpact will evalulate the simulation state per `communicate()` call and automatically generate audio.
        """
        self.auto: bool = auto
        # A dictionary of audio data. Key = Object ID; Value = `ObjectAudioStatic`.
        # These audio values will be applied to these objects instead of default values.
        self._static_audio_data_overrides: Dict[int, ObjectAudioStatic] = dict()
        if static_audio_data_overrides is not None:
            self._static_audio_data_overrides = static_audio_data_overrides
        """:field
        Collision events on this frame. Key = Object ID. Value = [`CollisionAudioEvent`](../physics_audio/collision_audio_event.md).
        """
        self.collision_events: Dict[int, CollisionAudioEvent] = dict()

        self._cached_audio_info: bool = False
        # A dictionary of audio data. Key = Object ID; Value = `ObjectAudioStatic`.
        self._static_audio_data: Dict[int, ObjectAudioStatic] = dict()

        # Summed scrape masters. Key = primary ID, secondary ID.
        self._scrape_summed_masters: Dict[Tuple[int, int], AudioSegment] = dict()
        # Keeping a track of previous scrape indices.
        self._scrape_previous_indices: Dict[Tuple[int, int], int] = dict()
        # Starting velocity magnitude of scraping object; use in calculating changing band-pass filter.
        self._scrape_start_velocities: Dict[Tuple[int, int], float] = dict()
        # Initialize the scraping event counter.
        self._scrape_events_count: Dict[Tuple[int, int], int] = dict()
        # Ignore collisions that include these object IDs.
        self._excluded_objects: List[int] = list()

        # Ongoing impact audio events. Key = Audio source ID. Value = Time of event.
        self._impact_events: Dict[int, float] = dict()
        self._min_time_between_impact_events: float = min_time_between_impact_events

    def get_initialization_commands(self) -> List[dict]:
        return [{"$type": "send_bounds"},
                {"$type": "send_rigidbodies",
                 "frequency": "always"},
                {"$type": "send_robot_joint_velocities",
                 "frequency": "always"},
                {"$type": "send_collisions",
                 "enter": True,
                 "exit": True,
                 "stay": True,
                 "collision_types": ["obj", "env"]},
                {"$type": "send_static_robots"},
                {"$type": "send_segmentation_colors"},
                {"$type": "send_static_rigidbodies"},
                {"$type": "send_static_oculus_touch"}]

    def on_send(self, resp: List[bytes]) -> None:
        super().on_send(resp=resp)
        # Cache static audio info.
        if not self._cached_audio_info:
            self._cached_audio_info = True
            self._cache_static_data(resp=resp)
        # Don't automatically generate audio.
        if not self.auto:
            return
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            # Mark this audio source as done.
            if r_id == "ausd":
                audio_source_id = AudioSourceDone(resp[i]).get_id()
                # The audio source might not be in this dictionary (for example if this was a scrape event).
                if audio_source_id in self._impact_events:
                    del self._impact_events[audio_source_id]
        # Get collision events.
        self._get_collision_types(resp=resp)
        for object_id in self.collision_events:
            command = None
            # Generate an impact sound.
            if self.collision_events[object_id].collision_type == CollisionAudioType.impact:
                # Generate an environment sound.
                if self.collision_events[object_id].secondary_id is None:
                    audio = self._static_audio_data[object_id]
                    command = self.get_impact_sound_command(velocity=self.collision_events[object_id].velocity,
                                                            contact_points=self.collision_events[object_id].collision.points,
                                                            contact_normals=self.collision_events[object_id].collision.normals,
                                                            primary_id=object_id,
                                                            primary_amp=audio.amp,
                                                            primary_material=audio.material.name + "_" + str(audio.size),
                                                            primary_mass=audio.mass,
                                                            secondary_id=None,
                                                            secondary_amp=PyImpact.FLOOR_AMP,
                                                            secondary_material=self._get_floor_material_name(),
                                                            secondary_mass=PyImpact.FLOOR_MASS,
                                                            primary_resonance=audio.resonance,
                                                            secondary_resonance=audio.resonance)
                # Generate an object sound.
                else:
                    target_audio = self._static_audio_data[self.collision_events[object_id].primary_id]
                    other_audio = self._static_audio_data[self.collision_events[object_id].secondary_id]
                    command = self.get_impact_sound_command(velocity=self.collision_events[object_id].velocity,
                                                            contact_points=self.collision_events[object_id].collision.points,
                                                            contact_normals=self.collision_events[object_id].collision.normals,
                                                            primary_id=target_audio.object_id,
                                                            primary_amp=target_audio.amp,
                                                            primary_material=target_audio.material.name + "_" + str(
                                                                target_audio.size),
                                                            primary_mass=target_audio.mass,
                                                            secondary_id=other_audio.object_id,
                                                            secondary_amp=other_audio.amp,
                                                            secondary_material=other_audio.material.name + "_" + str(
                                                                other_audio.size),
                                                            secondary_mass=other_audio.mass,
                                                            primary_resonance=target_audio.resonance,
                                                            secondary_resonance=other_audio.resonance)
            # Generate a scrape sound.
            elif self.collision_events[object_id].collision_type == CollisionAudioType.scrape and self.collision_events[object_id].secondary_id in self._scrape_objects:
                scrape_surface_id = self.collision_events[object_id].secondary_id
                # Generate an object sound.
                if scrape_surface_id is not None:
                    target_audio = self._static_audio_data[self.collision_events[object_id].primary_id]
                    other_audio = self._static_audio_data[self.collision_events[object_id].secondary_id]
                    command = self.get_scrape_sound_command(velocity=self.collision_events[object_id].velocity,
                                                            contact_points=self.collision_events[object_id].collision.points,
                                                            contact_normals=self.collision_events[object_id].collision.normals,
                                                            primary_id=target_audio.object_id,
                                                            primary_amp=target_audio.amp,
                                                            primary_material=target_audio.material.name + "_" + str(target_audio.size),
                                                            primary_mass=target_audio.mass,
                                                            secondary_id=other_audio.object_id,
                                                            secondary_amp=other_audio.amp,
                                                            secondary_material=other_audio.material.name + "_" + str(other_audio.size),
                                                            secondary_mass=other_audio.mass,
                                                            primary_resonance=target_audio.resonance,
                                                            secondary_resonance=other_audio.resonance,
                                                            scrape_material=self._scrape_objects[scrape_surface_id].scrape_material)
            # Append impact sound commands.
            if command is not None:
                self.commands.append(command)

    def _get_floor_material_name(self) -> str:
        """
        :return: The name of the floor material.
        """

        # We probably need dedicated wall and floor materials, or maybe they are in size category #6?
        # Setting to "4" for now, for general debugging purposes.
        return f"{self.floor.name}_{PyImpact.FLOOR_SIZE}"

    def _get_collision_types(self, resp: List[bytes]) -> None:
        """
        Get all collision types on this frame. Update previous area data.

        :param resp: The response from the build.
        """

        # Collision events per object on this frame. We'll only care about the most significant one.
        collision_events_per_object: Dict[int, List[CollisionAudioEvent]] = dict()
        # Get the previous areas.
        previous_areas: Dict[int, float] = {k: v.area for k, v in self.collision_events.items()}
        # Clear the collision events.
        self.collision_events.clear()
        rigidbody_data: Dict[int, Rigidbody] = dict()
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            # Get rigidbody data.
            if r_id == "rigi":
                rigidbodies = Rigidbodies(resp[i])
                for j in range(rigidbodies.get_num()):
                    rigidbody_data[rigidbodies.get_id(j)] = Rigidbody(velocity=rigidbodies.get_velocity(j),
                                                                      angular_velocity=rigidbodies.get_angular_velocity(j),
                                                                      sleeping=rigidbodies.get_sleeping(j))
            # Get robot joint velocity data.
            elif r_id == "rojv":
                robot_joint_velocities = RobotJointVelocities(resp[i])
                for j in range(robot_joint_velocities.get_num_joints()):
                    rigidbody_data[robot_joint_velocities.get_joint_id(j)] = Rigidbody(velocity=robot_joint_velocities.get_joint_velocity(j),
                                                                                       angular_velocity=robot_joint_velocities.get_joint_angular_velocity(j),
                                                                                       sleeping=robot_joint_velocities.get_joint_sleeping(j))
        # Get collision data.
        for object_ids in self.obj_collisions:
            collider_id = object_ids.int1
            collidee_id = object_ids.int2
            # Ignore this collision.
            if collider_id in self._excluded_objects or collidee_id in self._excluded_objects:
                continue
            event = CollisionAudioEvent(collision=self.obj_collisions[object_ids],
                                        object_0_static=self._static_audio_data[collider_id],
                                        object_0_dynamic=rigidbody_data[collider_id],
                                        object_1_static=self._static_audio_data[collidee_id],
                                        object_1_dynamic=rigidbody_data[collidee_id],
                                        previous_areas=previous_areas)
            # End an ongoing scrape, if any.
            if event.collision_type != CollisionAudioType.scrape:
                self._end_scrape((event.primary_id, event.secondary_id))
            if event.primary_id not in collision_events_per_object:
                collision_events_per_object[event.primary_id] = list()
            collision_events_per_object[event.primary_id].append(event)
        for object_id in self.env_collisions:
            if object_id in self._excluded_objects:
                continue
            event = CollisionAudioEvent(collision=self.env_collisions[object_id],
                                        object_0_static=self._static_audio_data[object_id],
                                        object_0_dynamic=rigidbody_data[object_id],
                                        previous_areas=previous_areas)
            # End an ongoing scrape, if any.
            if event.collision_type != CollisionAudioType.scrape:
                self._end_scrape((event.primary_id, event.secondary_id))
            if event.primary_id not in collision_events_per_object:
                collision_events_per_object[event.primary_id] = list()
            collision_events_per_object[event.primary_id].append(event)
        # Get the significant collision events per object.
        for primary_id in collision_events_per_object:
            events: List[CollisionAudioEvent] = [e for e in collision_events_per_object[primary_id] if e.magnitude > 0
                                                 and e.collision_type != CollisionAudioType.none]
            if len(events) > 0:
                event: CollisionAudioEvent = max(events, key=lambda x: x.magnitude)
                self.collision_events[event.primary_id] = event

    def _get_object_modes(self, material: Union[str, AudioMaterial]) -> Modes:
        """
        :param material: The audio material.

        :return: The audio modes.
        """
        data = self.material_data[material] if isinstance(material, str) else self.material_data[material.name]
        # Load the mode properties.
        f = -1
        p = -1
        t = -1
        for jm in range(0, 10):
            jf = 0
            while jf < 20:
                jf = data["cf"][jm] + self.rng.normal(0, data["cf"][jm] / 10)
            jp = data["op"][jm] + self.rng.normal(0, 10)
            jt = 0
            while jt < 0.001:
                jt = data["rt"][jm] + self.rng.normal(0, data["rt"][jm] / 10)
            if jm == 0:
                f = jf
                p = jp
                t = jt * 1e3
            else:
                f = np.append(f, jf)
                p = np.append(p, jp)
                t = np.append(t, jt * 1e3)
        return Modes(f, p, t)

    def get_impact_sound(self, velocity: np.ndarray, contact_normals: List[np.ndarray],
                         primary_id: int, primary_material: str, primary_amp: float, primary_mass: float,
                         secondary_id: Optional[int], secondary_material: str, secondary_amp: float,
                         secondary_mass: float, primary_resonance: float, secondary_resonance: float) -> Optional[Base64Sound]:
        """
        Produce sound of two colliding objects as a byte array.

        :param primary_id: The object ID for the primary (target) object.
        :param primary_material: The material label for the primary (target) object.
        :param secondary_id: The object ID for the secondary (other) object.
        :param secondary_material: The material label for the secondary (other) object.
        :param primary_amp: Sound amplitude of primary (target) object.
        :param secondary_amp: Sound amplitude of the secondary (other) object.
        :param primary_resonance: The resonance of the primary (target) object.
        :param secondary_resonance: The resonance of the secondary (other) object.
        :param velocity: The velocity.
        :param contact_normals: The collision contact normals.
        :param primary_mass: The mass of the primary (target) object.
        :param secondary_mass: The mass of the secondary (target) object.

        :return Sound data as a Base64Sound object.
        """

        # The sound amplitude of object 2 relative to that of object 1.
        amp2re1 = secondary_amp / primary_amp

        # Set the object modes.
        if secondary_id not in self.object_modes:
            self.object_modes.update({secondary_id: {}})
        if primary_id not in self.object_modes[secondary_id]:
            self.object_modes[secondary_id].update({primary_id: CollisionAudioInfo(self._get_object_modes(secondary_material),
                                                                                   self._get_object_modes(
                                                                                       primary_material),
                                                                                   amp=primary_amp * self.initial_amp)})
        # Unpack useful parameters.
        speed = np.square(velocity)
        speed = np.sum(speed)
        speed = math.sqrt(speed)
        nvel = velocity / np.linalg.norm(velocity)
        nspd = []
        for jc in range(len(contact_normals)):
            tmp = np.asarray(contact_normals[jc])
            tmp = tmp / np.linalg.norm(tmp)
            tmp = np.arccos(np.clip(np.dot(tmp, nvel), -1.0, 1.0))
            # Scale the speed by the angle (i.e. we want speed Normal to the surface).
            tmp = speed * np.cos(tmp)
            nspd.append(tmp)
        normal_speed = np.mean(nspd)
        mass = np.min([primary_mass, secondary_mass])

        # Re-scale the amplitude.
        if self.object_modes[secondary_id][primary_id].count == 0:
            # Sample the modes.
            sound, modes_1, modes_2 = self._make_impact_audio(amp2re1, mass,
                                                              mat1=primary_material,
                                                              mat2=secondary_material,
                                                              id1=primary_id,
                                                              id2=secondary_id,
                                                              primary_resonance=primary_resonance,
                                                              secondary_resonance=secondary_resonance)
            # Save collision info - we will need for later collisions.
            amp = self.object_modes[secondary_id][primary_id].amp
            self.object_modes[secondary_id][primary_id].init_speed = normal_speed
            self.object_modes[secondary_id][primary_id].obj1_modes = modes_1
            self.object_modes[secondary_id][primary_id].obj2_modes = modes_2

        else:
            amp = self.object_modes[secondary_id][primary_id].amp * normal_speed / self.object_modes[secondary_id][primary_id].init_speed
            # Adjust modes here so that two successive impacts are not identical.
            modes_1 = self.object_modes[secondary_id][primary_id].obj1_modes
            modes_2 = self.object_modes[secondary_id][primary_id].obj2_modes
            modes_1.powers = modes_1.powers + self.rng.normal(0, 2, len(modes_1.powers))
            modes_2.powers = modes_2.powers + self.rng.normal(0, 2, len(modes_2.powers))
            sound = PyImpact._synth_impact_modes(modes_1, modes_2, mass, primary_resonance, secondary_resonance)
            self.object_modes[secondary_id][primary_id].obj1_modes = modes_1
            self.object_modes[secondary_id][primary_id].obj2_modes = modes_2

        if self.logging:
            mode_props = dict()
            self._log_modes(self.object_modes[secondary_id][primary_id].count, mode_props, primary_id, secondary_id,
                            modes_1, modes_2, amp, primary_material, secondary_material)

        # On rare occasions, it is possible for PyImpact to fail to generate a sound.
        if sound is None:
            return None

        # Count the collisions.
        self.object_modes[secondary_id][primary_id].count_collisions()

        # Prevent distortion by clamping the amp.
        if self.prevent_distortion and np.abs(amp) > 0.99:
            amp = 0.99

        sound = amp * sound / np.max(np.abs(sound))
        return Base64Sound(sound)

    def get_impact_sound_command(self, velocity: np.ndarray, contact_points: List[np.ndarray],
                                 contact_normals: List[np.ndarray], primary_id: int,
                                 primary_material: str, primary_amp: float, primary_mass: float,
                                 secondary_id: Optional[int], secondary_material: str, secondary_amp: float,
                                 secondary_mass: float, primary_resonance: float, secondary_resonance: float) -> Optional[dict]:
        """
        Create an impact sound, and return a valid command to play audio data in TDW.
        "target" should usually be the smaller object, which will play the sound.
        "other" should be the larger (stationary) object.

        :param primary_id: The object ID for the primary (target) object.
        :param primary_material: The material label for the primary (target) object.
        :param secondary_id: The object ID for the secondary (other) object.
        :param secondary_material: The material label for the secondary (other) object.
        :param primary_amp: Sound amplitude of primary (target) object.
        :param secondary_amp: Sound amplitude of the secondary (other) object.
        :param primary_resonance: The resonance of the primary (target) object.
        :param secondary_resonance: The resonance of the secondary (other) object.
        :param velocity: The velocity.
        :param contact_points: The collision contact points.
        :param contact_normals: The collision contact normals.
        :param primary_mass: The mass of the primary (target) object.
        :param secondary_mass: The mass of the secondary (target) object.

        :return A `play_audio_data` or `play_point_source_data` command that can be sent to the build via `Controller.communicate()`.
        """

        sound = self.get_impact_sound(velocity=velocity, contact_normals=contact_normals, primary_id=primary_id,
                                      primary_material=primary_material, primary_amp=primary_amp,
                                      primary_mass=primary_mass, secondary_id=secondary_id,
                                      secondary_material=secondary_material, secondary_amp=secondary_amp,
                                      secondary_mass=secondary_mass, primary_resonance=primary_resonance, secondary_resonance=secondary_resonance)
        if sound is not None:
            if primary_id not in self._impact_events:
                self._impact_events[primary_id] = time()
                return self._get_audio_command(audio_source_id=primary_id, contact_points=contact_points, sound=sound)
            # Don't play too many impact events to avoid a droning effect.
            elif time() - self._impact_events[primary_id] < self._min_time_between_impact_events:
                return None
            else:
                return self._get_audio_command(audio_source_id=primary_id, contact_points=contact_points, sound=sound)
        # If PyImpact failed to generate a sound (which is rare!), fail silently here.
        else:
            return None

    def _make_impact_audio(self, amp2re1: float, mass: float, id1: int, id2: int, primary_resonance: float,
                           secondary_resonance: float, mat1: str = 'cardboard', mat2: str = 'cardboard') -> (np.array, Modes, Modes):
        """
        Generate an impact sound.

        :param mat1: The material label for one of the colliding objects.
        :param mat2: The material label for the other object.
        :param amp2re1: The sound amplitude of object 2 relative to that of object 1.
        :param mass: The mass of the smaller of the two colliding objects.
        :param id1: The ID for the one of the colliding objects.
        :param id2: The ID for the other object.
        :param primary_resonance: The resonance of one of the colliding objects.
        :param secondary_resonance: The resonance of the other object.

        :return The sound, and the object modes.
        """

        # Unpack material names.
        for jmat in AudioMaterial:
            if mat1 == jmat:
                tmp1 = jmat
                mat1 = tmp1.name
            if mat2 == jmat:
                tmp2 = jmat
                mat2 = tmp2.name
        # Sample modes of object1.
        modes_1 = self.object_modes[id2][id1].obj1_modes
        modes_2 = self.object_modes[id2][id1].obj2_modes
        # Scale the two sounds as specified.
        modes_2.decay_times = modes_2.decay_times + 20 * np.log10(amp2re1)
        snth = PyImpact._synth_impact_modes(modes_1, modes_2, mass, primary_resonance, secondary_resonance)
        return snth, modes_1, modes_2

    def _get_impulse_response(self, velocity: np.ndarray, contact_normals: List[np.ndarray], primary_id: int,
                              primary_material: str, primary_amp: float, primary_mass: float,
                              secondary_id: int, secondary_material: str, secondary_amp: float, secondary_mass: float,
                              primary_resonance: float, secondary_resonance: float) -> Tuple[np.ndarray, float]:
        """
        Generate an impulse response from the modes for two specified objects.

        :param primary_id: The object ID for the primary (target) object.
        :param primary_material: The material label for the primary (target) object.
        :param secondary_id: The object ID for the secondary (other) object.
        :param secondary_material: The material label for the secondary (other) object.
        :param primary_amp: Sound amplitude of primary (target) object.
        :param secondary_amp: Sound amplitude of the secondary (other) object.
        :param primary_resonance: The resonance of the primary (target) object.
        :param secondary_resonance: The resonances of the secondary (other) object.
        :param velocity: The velocity.
        :param contact_normals: The collision contact normals.
        :param primary_mass: The mass of the primary (target) object.
        :param secondary_mass: The mass of the secondary (target) object.

        :return The impulse response and the frequency.
        """

        self.get_impact_sound(velocity=velocity, contact_normals=contact_normals, primary_id=primary_id,
                              primary_material=primary_material, primary_amp=primary_amp, primary_mass=primary_mass,
                              secondary_id=secondary_id, secondary_material=secondary_material,
                              secondary_amp=secondary_amp, secondary_mass=secondary_mass, primary_resonance=primary_resonance, secondary_resonance=secondary_resonance)

        modes_1 = self.object_modes[secondary_id][primary_id].obj1_modes
        modes_2 = self.object_modes[secondary_id][primary_id].obj2_modes
        h1 = modes_1.sum_modes(resonance=primary_resonance)
        h2 = modes_2.sum_modes(resonance=secondary_resonance)
        h = Modes.mode_add(h1, h2)
        return h, min(modes_1.frequencies)

    def get_scrape_sound_command(self, velocity: np.ndarray, contact_points: np.ndarray,
                                 contact_normals: List[np.ndarray], primary_id: int,
                                 primary_material: str, primary_amp: float, primary_mass: float,
                                 secondary_id: Optional[int], secondary_material: str, secondary_amp: float,
                                 secondary_mass: float, primary_resonance: float, secondary_resonance: float,
                                 scrape_material: ScrapeMaterial) -> Optional[dict]:
        """
        :param primary_id: The object ID for the primary (target) object.
        :param primary_material: The material label for the primary (target) object.
        :param secondary_id: The object ID for the secondary (other) object.
        :param secondary_material: The material label for the secondary (other) object.
        :param primary_amp: Sound amplitude of primary (target) object.
        :param secondary_amp: Sound amplitude of the secondary (other) object.
        :param primary_resonance: The resonance of the primary (target) object.
        :param secondary_resonance: The resonance of the secondary (other) object.
        :param velocity: The velocity.
        :param contact_points: The collision contact points.
        :param contact_normals: The collision contact normals.
        :param primary_mass: The mass of the primary (target) object.
        :param secondary_mass: The mass of the secondary (target) object.
        :param scrape_material: The [scrape material](../physics_audio/scrape_material.md).

        :return A command to play a scrape sound.
        """

        sound = self.get_scrape_sound(velocity=velocity,
                                      contact_normals=contact_normals,
                                      primary_id=primary_id,
                                      primary_material=primary_material,
                                      primary_amp=primary_amp,
                                      primary_mass=primary_mass,
                                      secondary_id=secondary_id,
                                      secondary_material=secondary_material,
                                      secondary_amp=secondary_amp,
                                      secondary_mass=secondary_mass,
                                      primary_resonance=primary_resonance,
                                      secondary_resonance=secondary_resonance,
                                      scrape_material=scrape_material)
        if sound is None:
            return None
        else:
            # Use random audio source IDs so that multiple scrape sound chunks can play at the same time.
            return self._get_audio_command(audio_source_id=int.from_bytes(urandom(3), byteorder='big'),
                                           contact_points=contact_points,
                                           sound=sound)

    def get_scrape_sound(self, velocity: np.ndarray, contact_normals: List[np.ndarray], primary_id: int,
                         primary_material: str, primary_amp: float, primary_mass: float,
                         secondary_id: int, secondary_material: str, secondary_amp: float, secondary_mass: float,
                         primary_resonance: float, secondary_resonance: float, scrape_material: ScrapeMaterial) -> Optional[Base64Sound]:
        """
        Create a scrape sound, and return a valid command to play audio data in TDW.
        "target" should usually be the smaller object, which will play the sound.
        "other" should be the larger (stationary) object.

        :param primary_id: The object ID for the primary (target) object.
        :param primary_material: The material label for the primary (target) object.
        :param secondary_id: The object ID for the secondary (other) object.
        :param secondary_material: The material label for the secondary (other) object.
        :param primary_amp: Sound amplitude of primary (target) object.
        :param secondary_amp: Sound amplitude of the secondary (other) object.
        :param primary_resonance: The resonance of the primary (target) object.
        :param secondary_resonance: The resonance of the secondary (other) object.
        :param velocity: The velocity.
        :param contact_normals: The collision contact normals.
        :param primary_mass: The mass of the primary (target) object.
        :param secondary_mass: The mass of the secondary (target) object.
        :param scrape_material: The [scrape material](../physics_audio/scrape_material.md).

        :return A [`Base64Sound`](../physics_audio/base64_sound.md) object or None if no sound.
        """

        scrape_key: Tuple[int, int] = (primary_id, secondary_id)
        if scrape_key not in self._scrape_previous_indices:
            self._scrape_previous_indices[scrape_key] = 0

        # Initialize scrape variables; if this is an in=process scrape, these will be replaced bu te stored values.
        summed_master = AudioSegment.silent(duration=2000, frame_rate=SAMPLE_RATE)
        scrape_event_count = 0

        # Is this a new scrape?
        if scrape_key in self._scrape_summed_masters:
            summed_master = self._scrape_summed_masters[scrape_key]
            scrape_event_count = self._scrape_events_count[scrape_key]
        else:
            # No -- add initialized values to dictionaries.
            self._scrape_summed_masters[scrape_key] = summed_master
            self._scrape_events_count[scrape_key] = scrape_event_count

        # Get magnitude of velocity of the scraping object.
        mag = min(np.linalg.norm(velocity), PyImpact.SCRAPE_MAX_VELOCITY)

        # Cache the starting velocity.
        if scrape_event_count == 0:
            self._scrape_start_velocities[scrape_key] = mag

        # Map magnitude to gain level -- decrease in velocity = rise in negative dB, i.e. decrease in gain.
        db2 = 40 * np.log10(mag / PyImpact.SCRAPE_MAX_VELOCITY) - 4
        db1 = 20 * np.log10(mag / PyImpact.SCRAPE_MAX_VELOCITY) - 25

        # Get impulse response of the colliding objects. Amp values would normally come from objects.csv.
        # We also get the lowest-frequency IR mode, which we use to set the high-pass filter cutoff below.
        scraping_ir, min_mode_freq = self._get_impulse_response(velocity=velocity,
                                                                contact_normals=contact_normals,
                                                                primary_id=primary_id,
                                                                primary_material=primary_material,
                                                                primary_amp=primary_amp,
                                                                primary_mass=primary_mass,
                                                                secondary_id=secondary_id,
                                                                secondary_material=secondary_material,
                                                                secondary_amp=secondary_amp,
                                                                secondary_mass=secondary_mass,
                                                                primary_resonance=primary_resonance,
                                                                secondary_resonance=secondary_resonance)
        # Cache the scrape material.
        # Don't do this when PyImpact is initialized because scrape surfaces are large files!
        # We don't want them in memory all the time and they can be a bit slow to load.
        if scrape_material not in self.scrape_surface_data:
            scrape_surface = np.load(str(
                Path(resource_filename(__name__, f"py_impact/scrape_surfaces/{scrape_material.name}.npy")).resolve()))
            for i in range(2):
                scrape_surface = np.append(scrape_surface, scrape_surface)
            #   Load the surface texture as a 1D vector
            #   Create surface texture of desired length
            #   Calculate first and second derivatives by first principles
            #   Apply non-linearity on the second derivative
            #   Apply a variable Gaussian average
            #   Calculate the horizontal and vertical forces
            #   Convolve the force with the impulse response
            scrape_surface = gaussian_filter1d(scrape_surface, 5)
            dsdx = (scrape_surface[1:] - scrape_surface[0:-1]) / PyImpact.SCRAPE_M_PER_PIXEL
            d2sdx2 = (dsdx[1:] - dsdx[0:-1]) / PyImpact.SCRAPE_M_PER_PIXEL
            rough_ratio = (np.std(scrape_surface) / (3 * 10 ** -4)) ** 1
            r_gain = 20 * np.log10(rough_ratio)
            self.scrape_surface_data[scrape_material] = {"dsdx": dsdx,
                                                         "d2sdx2": d2sdx2,
                                                         "surface": scrape_surface,
                                                         "r_gain": r_gain}
        dist = mag / 10
        num_pts = int(np.floor(dist / PyImpact.SCRAPE_M_PER_PIXEL) + 1)
        # No scrape.
        if num_pts < 1:
            self._end_scrape(scrape_key)
            return None
        # interpolate the surface slopes and curvatures based on the velocity magnitude
        final_ind = self._scrape_previous_indices[scrape_key] + num_pts

        vect1 = np.linspace(0, 1, num_pts)
        vect2 = np.linspace(0, 1, 4410)

        if final_ind > len(self.scrape_surface_data[scrape_material]["surface"]) - 1:
            self._scrape_previous_indices[scrape_key] = 0
            final_ind = num_pts
        slope_int = np.interp(vect2, vect1, self.scrape_surface_data[scrape_material]["dsdx"][
                                            self._scrape_previous_indices[scrape_key]:final_ind])
        curve_int = np.interp(vect2, vect1, self.scrape_surface_data[scrape_material]["d2sdx2"][
                                            self._scrape_previous_indices[scrape_key]:final_ind])
        self._scrape_previous_indices[scrape_key] = final_ind

        curve_int_tan = np.tanh(curve_int / (1000 * primary_mass))

        d2_section = uniform_filter1d(curve_int_tan, 5)

        vert_force = d2_section
        hor_force = slope_int

        t_force2 = vert_force / max(np.abs(vert_force))
        t_force1 = hor_force[:len(vert_force)]

        conv1 = sg.fftconvolve(scraping_ir, t_force1)
        conv2 = sg.fftconvolve(scraping_ir, t_force2)

        # Again, we need this as an AudioSegment for overlaying with the previous frame's segment.
        # Convert to 16-bit integers for Unity, normalizing to make sure to minimize loss of precision from truncating floating values.
        normalized_noise_ints_conv1 = PyImpact._normalize_16bit_int(conv1)
        noise_seg_conv1 = AudioSegment(normalized_noise_ints_conv1.tobytes(),
                                       frame_rate=SAMPLE_RATE,
                                       sample_width=SAMPLE_WIDTH,
                                       channels=CHANNELS)

        normalized_noise_ints_conv2 = PyImpact._normalize_16bit_int(conv2)
        noise_seg_conv2 = AudioSegment(normalized_noise_ints_conv2.tobytes(),
                                       frame_rate=SAMPLE_RATE,
                                       sample_width=SAMPLE_WIDTH,
                                       channels=CHANNELS)

        # Gain-adjust the convolved segment using db value computed earlier.
        noise_seg_conv1 = noise_seg_conv1.apply_gain(db1)
        noise_seg_conv2 = noise_seg_conv2.apply_gain(db2)

        noise_seg_conv = noise_seg_conv1.overlay(noise_seg_conv2)
        # Apply roughness gain.
        noise_seg_conv = noise_seg_conv.apply_gain(self.scrape_surface_data[scrape_material]["r_gain"])

        # Pad the end of master with 100ms of silence, the start of the current segment with (n * 100ms) of silence, and overlay.
        summed_master = summed_master + PyImpact.SILENCE_100MS
        summed_master = summed_master.overlay(noise_seg_conv, position=100 * scrape_event_count)
        # Extract 100ms "chunk" of sound to send over to Unity.
        start_idx = 100 * scrape_event_count
        unity_chunk = summed_master[start_idx:start_idx + 100]
        # Update stored summed waveform.
        self._scrape_summed_masters[scrape_key] = summed_master

        # Update scrape event count.
        scrape_event_count += 1
        self._scrape_events_count[scrape_key] = scrape_event_count
        # Scrape data is handled differently than impact data, so we'll create a dummy object first.
        sound = Base64Sound(np.array([0]))
        # Set the audio data.
        sound.wav_str = base64.b64encode(unity_chunk.raw_data).decode()
        sound.length = len(unity_chunk.raw_data)
        sound.bytes = unity_chunk.raw_data
        return sound

    @staticmethod
    def _synth_impact_modes(modes1: Modes, modes2: Modes, mass: float, primary_resonance: float, secondary_resonance: float) -> np.ndarray:
        """
        Generate an impact sound from specified modes for two objects, and the mass of the smaller object.

        :param modes1: Modes of object 1. A numpy array with: column1=mode frequencies (Hz); column2=mode onset powers in dB; column3=mode RT60s in milliseconds;
        :param modes2: Modes of object 2. Formatted as modes1/modes2.
        :param mass: the mass of the smaller of the two colliding objects.
        :param primary_resonance: The resonance of the object 1.
        :param secondary_resonance: The resonance of the object 2.

        :return The impact sound.
        """

        h1 = modes1.sum_modes(resonance=primary_resonance)
        h2 = modes2.sum_modes(resonance=secondary_resonance)
        h = Modes.mode_add(h1, h2)
        if len(h) == 0:
            return None
        # Convolve with force, with contact time scaled by the object mass.
        max_t = 0.001 * mass
        # A contact time over 2ms is unphysically long.
        max_t = np.min([max_t, 2e-3])
        n_pts = int(np.ceil(max_t * 44100))
        tt = np.linspace(0, np.pi, n_pts)
        frc = np.sin(tt)
        x = sg.fftconvolve(h, frc)
        x = x / abs(np.max(x))
        return x

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
        elif s <= 10:
            return 5
        else:
            return 6

    def reset(self, initial_amp: float = 0.5, static_audio_data_overrides: Dict[int, ObjectAudioStatic] = None,
              scrape_objects: Dict[int, ScrapeModel] = None) -> None:
        """
        Reset PyImpact. This is somewhat faster than creating a new PyImpact object per trial.

        :param initial_amp: The initial amplitude, i.e. the "master volume". Must be > 0 and < 1.
        :param static_audio_data_overrides: If not None, a dictionary of audio data. Key = Object ID; Value = [`ObjectAudioStatic`](../physics_audio/object_audio_static.md). These audio values will be applied to these objects instead of default values.
        :param scrape_objects: A dictionary of [scrape objects](../physics_audio/scrape_model.md) in the scene. Key = Object ID. Ignored if None or `scrape == False` in the constructor.
        """

        assert 0 < initial_amp < 1, f"initial_amp is {initial_amp} (must be > 0 and < 1)."
        self._cached_audio_info = False
        self.initialized = False
        self._static_audio_data.clear()
        self._static_audio_data_overrides.clear()
        self._scrape_objects.clear()
        # Use scrape surfaces.
        if self._scrape and scrape_objects is not None:
            for k in scrape_objects:
                self._scrape_objects[k] = scrape_objects[k]
        if static_audio_data_overrides is not None:
            for k in static_audio_data_overrides:
                self._static_audio_data_overrides[k] = static_audio_data_overrides[k]
        # Clear the object data.
        self.object_modes.clear()
        # Clear collision data.
        self.collision_events.clear()
        # Clear scrape data.
        self._scrape_summed_masters.clear()
        self._scrape_start_velocities.clear()
        self._scrape_events_count.clear()
        self._scrape_previous_indices.clear()
        self._excluded_objects.clear()
        # Clear impact count.
        self._impact_events.clear()
        # Clear ongoing commands.
        self.commands.clear()
        # Stop all ongoing audio.
        self.commands.append({"$type": "stop_all_audio"})

    def _log_modes(self, count: int, mode_props: dict, id1: int, id2: int, modes_1: Modes, modes_2: Modes, amp: float, mat1: str, mat2: str):
        """
        Log mode properties info for a single collision event.

        :param count: Mode count for this material-material collision.
        :param mode_props: Dictionary to log to.
        :param id1: ID of the "other" object.
        :param id2: ID of the "target" object.
        :param modes_1: Modes of the "other" object.
        :param modes_2: Modes of the "target" object.
        :param amp: Adjusted amplitude value of collision.
        :param mat1: Material of the "other" object.
        :param mat2: Material of the "target" object.
        """

        mode_props["modes_count"] = count
        mode_props["other_id"] = id1
        mode_props["target_id"] = id2
        mode_props["amp"] = amp
        mode_props["other_material"] = mat1
        mode_props["target_material"] = mat2
        mode_props["modes_1.frequencies"] = modes_1.frequencies.tolist()
        mode_props["modes_1.powers"] = modes_1.powers.tolist()
        mode_props["modes_1.decay_times"] = modes_1.decay_times.tolist()
        mode_props["modes_2.frequencies"] = modes_2.frequencies.tolist()
        mode_props["modes_2.powers"] = modes_2.powers.tolist()
        mode_props["modes_2.decay_times"] = modes_2.decay_times.tolist()
        self.mode_properties_log[str(id1) + "_" + str(id2) + "__" + str(count)] = mode_props

    def _cache_static_data(self, resp: List[bytes]) -> None:
        """
        Cache static data.

        :param resp: The response from the build.
        """

        # Load the default object info.
        categories: Dict[int, str] = dict()
        names: Dict[int, str] = dict()
        robot_joints: Dict[int, dict] = dict()
        object_masses: Dict[int, float] = dict()
        object_bouncinesses: Dict[int, float] = dict()
        extents: Dict[int, np.ndarray] = dict()
        vr_nodes: List[ObjectAudioStatic] = list()
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
                    if self._scrape and (model_name in DEFAULT_SCRAPE_MODELS or object_id in self._scrape_objects):
                        if object_id not in self._scrape_objects:
                            self._scrape_objects[object_id] = DEFAULT_SCRAPE_MODELS[model_name]
                        # Add the visual material.
                        material_record = PyImpact.__VISUAL_MATERIAL_LIBRARIAN.get_record(
                            name=self._scrape_objects[object_id].visual_material)
                        self.commands.append({"$type": "add_material",
                                              "name": material_record.name,
                                              "url": material_record.get_url()})
                        # Set the visual material.
                        for sub_object in self._scrape_objects[object_id].sub_objects:
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
                    object_bouncinesses[srig.get_id(j)] = srig.get_bounciness(j)
            # Add VR nodes.
            elif r_id == "soct":
                soct = StaticOculusTouch(resp[i])
                if soct.get_human_hands():
                    vr_material = PyImpact.VR_HUMAN_MATERIAL
                    vr_bounciness = PyImpact.VR_HUMAN_BOUNCINESS
                else:
                    vr_material = PyImpact.ROBOT_JOINT_MATERIAL
                    vr_bounciness = PyImpact.ROBOT_JOINT_BOUNCINESS
                for vr_id, vr_name in zip([soct.get_body_id(), soct.get_left_hand_id(), soct.get_right_hand_id()],
                                          ["vr_node_body", "vr_node_left_hand", "vr_node_right_hand"]):
                    vr_nodes.append(ObjectAudioStatic(name=vr_name,
                                                      mass=10,
                                                      material=vr_material,
                                                      bounciness=vr_bounciness,
                                                      resonance=PyImpact.DEFAULT_RESONANCE,
                                                      size=PyImpact.DEFAULT_SIZE,
                                                      amp=PyImpact.DEFAULT_AMP,
                                                      object_id=vr_id))
                    self._excluded_objects.append(vr_id)
        need_to_derive: List[int] = list()
        for object_id in names:
            name = names[object_id]
            # Use override data.
            if object_id in self._static_audio_data_overrides:
                self._static_audio_data[object_id] = self._static_audio_data_overrides[object_id]
                self._static_audio_data[object_id].mass = object_masses[object_id]
                self._static_audio_data[object_id].object_id = object_id
            # Use default audio data.
            elif name in DEFAULT_OBJECT_AUDIO_STATIC_DATA:
                self._static_audio_data[object_id] = DEFAULT_OBJECT_AUDIO_STATIC_DATA[name]
                self._static_audio_data[object_id].mass = object_masses[object_id]
                self._static_audio_data[object_id].object_id = object_id
            else:
                need_to_derive.append(object_id)
        current_values = self._static_audio_data.values()
        derived_data: Dict[int, ObjectAudioStatic] = dict()
        for object_id in need_to_derive:
            # Fallback option: comparable objects in the same category.
            objects_in_same_category = [o for o in categories if categories[o] == categories[object_id]]
            if len(objects_in_same_category) > 0:
                amps: List[float] = [a.amp for a in current_values]
                materials: List[AudioMaterial] = [a.material for a in current_values]
                resonances: List[float] = [a.resonance for a in current_values]
            # Fallback option: Find objects with similar volume.
            else:
                amps: List[float] = list()
                materials: List[AudioMaterial] = list()
                resonances: List[float] = list()
                for m_id in object_masses:
                    if m_id == object_id or m_id not in self._static_audio_data:
                        continue
                    if np.abs(object_masses[m_id] / object_masses[object_id]) < 1.5:
                        amps.append(self._static_audio_data[m_id].amp)
                        materials.append(self._static_audio_data[m_id].material)
                        resonances.append(self._static_audio_data[m_id].resonance)
            # Fallback option: Use default values.
            if len(amps) == 0:
                amp: float = PyImpact.DEFAULT_AMP
                material: AudioMaterial = PyImpact.DEFAULT_MATERIAL
                resonance: float = PyImpact.DEFAULT_RESONANCE
            # Get averages or maximums of each value.
            else:
                amp: float = round(sum(amps) / len(amps), 3)
                material: AudioMaterial = max(set(materials), key=materials.count)
                resonance: float = round(sum(resonances) / len(resonances), 3)
            derived_data[object_id] = ObjectAudioStatic(name=names[object_id],
                                                        mass=object_masses[object_id],
                                                        material=material,
                                                        bounciness=object_bouncinesses[object_id],
                                                        resonance=resonance,
                                                        size=self.get_size(model=extents[object_id]),
                                                        amp=amp,
                                                        object_id=object_id)
        # Add the derived data.
        for object_id in derived_data:
            self._static_audio_data[object_id] = derived_data[object_id]
        # Add robot joints.
        for joint_id in robot_joints:
            self._static_audio_data[joint_id] = ObjectAudioStatic(name=robot_joints[joint_id]["name"],
                                                                  mass=robot_joints[joint_id]["mass"],
                                                                  material=PyImpact.ROBOT_JOINT_MATERIAL,
                                                                  bounciness=PyImpact.ROBOT_JOINT_BOUNCINESS,
                                                                  resonance=PyImpact.DEFAULT_RESONANCE,
                                                                  size=PyImpact.DEFAULT_SIZE,
                                                                  amp=PyImpact.DEFAULT_AMP,
                                                                  object_id=joint_id)
        # Add VR nodes.
        for vr_node in vr_nodes:
            self._static_audio_data[vr_node.object_id] = vr_node

    @staticmethod
    def _normalize_16bit_int(arr: np.ndarray) -> np.ndarray:
        """
        Convert numpy float array to normalized 16-bit integers.

        :param arr: Numpy float data to convert.

        :return: The converted numpy array.
        """

        normalized_floats = PyImpact._normalize_floats(arr)

        return (normalized_floats * 32767).astype(np.int16)

    @staticmethod
    def _normalize_floats(arr: np.ndarray) -> np.ndarray:
        """
        Normalize numpy array of float audio data.

        :param arr: Numpy float data to normalize.

        :return The normalized array.
        """

        if np.all(arr == 0):
            return arr
        else:
            return arr / np.abs(arr).max()

    def _end_scrape(self, scrape_key: Tuple[int, int]) -> None:
        """
        Clean up after a given scrape event has ended.

        :param: The scrape index key.
        """

        if scrape_key in self._scrape_events_count:
            del self._scrape_events_count[scrape_key]
        if scrape_key in self._scrape_summed_masters:
            del self._scrape_summed_masters[scrape_key]
        if scrape_key in self._scrape_start_velocities:
            del self._scrape_start_velocities[scrape_key]
        if scrape_key in self._scrape_previous_indices:
            del self._scrape_previous_indices[scrape_key]

    def _get_audio_command(self, audio_source_id: int, contact_points: np.ndarray, sound: Base64Sound) -> dict:
        """
        :param audio_source_id: The audio source ID.
        :param contact_points: The collision contact points.
        :param sound: The Base64Sound object.

        :return: A command to play audio data.
        """

        point = np.mean(contact_points, axis=0)
        return {"$type": "play_audio_data" if not self.resonance_audio else "play_point_source_data",
                "id": audio_source_id,
                "position": {"x": float(point[0]), "y": float(point[1]), "z": float(point[2])},
                "num_frames": sound.length,
                "num_channels": CHANNELS,
                "frame_rate": SAMPLE_RATE,
                "wav_data": sound.wav_str}
