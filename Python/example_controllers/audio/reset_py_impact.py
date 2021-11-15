import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.resonance_audio_initializer import ResonanceAudioInitializer
from tdw.add_ons.py_impact import PyImpact
from tdw.physics_audio.object_audio_static import ObjectAudioStatic
from tdw.physics_audio.audio_material import AudioMaterial
from tdw.physics_audio.audio_material_constants import DYNAMIC_FRICTION, STATIC_FRICTION


class ResetPyImpact(Controller):
    """
    Reset `PyImpact` between trials.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.rng: np.random.RandomState = np.random.RandomState(0)

        # Add a camera.
        camera = ThirdPersonCamera(position={"x": 1, "y": 1.7, "z": -0.5},
                                   look_at={"x": 0, "y": 0.5, "z": 0},
                                   avatar_id="a")
        resonance_audio_floor = "parquet"
        py_impact_floor = ResonanceAudioInitializer.AUDIO_MATERIALS[resonance_audio_floor]
        # Initialize audio.
        audio_initializer = ResonanceAudioInitializer(avatar_id="a", floor=resonance_audio_floor)
        # Initialize PyImpact, using the controller's RNG.
        self.py_impact = PyImpact(initial_amp=0.5, floor=py_impact_floor, rng=self.rng, resonance_audio=True)
        # Initialize the scene.
        self.add_ons.extend([camera, audio_initializer, self.py_impact])
        self.communicate(TDWUtils.create_empty_room(7, 7))

    def trial(self) -> None:
        # Set the parameters for initializing the object.
        object_id: int = self.get_unique_id()
        object_name: str = "vase_02"
        object_mass: float = float(self.rng.uniform(0.5, 0.8))
        object_bounciness: float = float(self.rng.uniform(0.5, 0.7))
        object_material = AudioMaterial.wood_soft
        static_audio_data = ObjectAudioStatic(name=object_name,
                                              object_id=object_id,
                                              mass=object_mass,
                                              bounciness=object_bounciness,
                                              amp=0.6,
                                              resonance=0.45,
                                              size=1,
                                              material=object_material)
        # Reset PyImpact.
        self.py_impact.reset(static_audio_data_overrides={object_id: static_audio_data})
        # Add the object.
        self.communicate(self.get_add_physics_object(model_name=object_name,
                                                     position={"x": 0, "y": float(self.rng.uniform(3, 4)), "z": 0},
                                                     object_id=object_id,
                                                     default_physics_values=False,
                                                     mass=object_mass,
                                                     dynamic_friction=DYNAMIC_FRICTION[object_material],
                                                     static_friction=STATIC_FRICTION[object_material],
                                                     bounciness=object_bounciness))
        # Let the object fall.
        for i in range(200):
            self.communicate([])
        # Destroy the object.
        self.communicate({"$type": "destroy_object",
                          "id": object_id})

    def run(self) -> None:
        for i in range(10):
            self.trial()
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = ResetPyImpact()
    c.run()
