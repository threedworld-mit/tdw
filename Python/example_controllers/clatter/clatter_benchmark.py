from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.benchmark import Benchmark
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.audio_initializer import AudioInitializer
from tdw.add_ons.clatter import Clatter
from tdw.physics_audio.impact_material import ImpactMaterial
from tdw.physics_audio.clatter_object import ClatterObject
from tdw.physics_audio.impact_material_constants import DYNAMIC_FRICTION, STATIC_FRICTION


class ClatterBenchmark(Controller):
    """
    Benchmark Clatter in TDW.
    """

    SPHERE: ClatterObject = ClatterObject(impact_material=ImpactMaterial.glass,
                                          size=0,
                                          amp=0.2,
                                          resonance=0.05)
    EXTENT: float = 0.5
    DIAMETER: float = 0.013
    SPACING: float = 0.1
    SPHERE_MASS: float = 0.03
    SPHERE_BOUNCINESS: float = 0.6
    SPHERE_Y: float = 0.6
    SPHERE_DYNAMIC_FRICTION: float = DYNAMIC_FRICTION[SPHERE.impact_material]
    SPHERE_STATIC_FRICTION: float = STATIC_FRICTION[SPHERE.impact_material]

    def trial(self) -> float:
        # Hard-reset all add-ons.
        self.add_ons.clear()
        commands = [{"$type": "load_scene",
                     "scene_name": "ProcGenScene"},
                    TDWUtils.create_empty_room(6, 6)]
        clatter_objects = dict()
        # Add spheres in a grid.
        object_id = 0
        z = -ClatterBenchmark.EXTENT
        while z < ClatterBenchmark.EXTENT:
            x = -ClatterBenchmark.EXTENT
            while x < ClatterBenchmark.EXTENT:
                # Add the object.
                commands.extend(Controller.get_add_physics_object(model_name="sphere",
                                                                  object_id=object_id,
                                                                  library="models_flex.json",
                                                                  position={"x": x, "y": ClatterBenchmark.SPHERE_Y, "z": z},
                                                                  default_physics_values=False,
                                                                  scale_factor={"x": ClatterBenchmark.DIAMETER,
                                                                                "y": ClatterBenchmark.DIAMETER,
                                                                                "z": ClatterBenchmark.DIAMETER},
                                                                  mass=ClatterBenchmark.SPHERE_MASS,
                                                                  bounciness=ClatterBenchmark.SPHERE_BOUNCINESS,
                                                                  static_friction=ClatterBenchmark.SPHERE_STATIC_FRICTION,
                                                                  dynamic_friction=ClatterBenchmark.SPHERE_DYNAMIC_FRICTION))
                # Remember the marble Clatter data.
                clatter_objects[object_id] = ClatterBenchmark.SPHERE
                # Increment the object ID.
                object_id += 1
                x += ClatterBenchmark.SPACING
            z += ClatterBenchmark.SPACING
        # Create the camera.
        camera = ThirdPersonCamera(avatar_id="a",
                                   position={"x": 1, "y": 1, "z": -1},
                                   look_at={"x": 0, "y": 0.5, "z": 0})
        # Initialize audio.
        audio = AudioInitializer(avatar_id=camera.avatar_id)
        # Create the Clatter add-on. Add the object data overrides and set the environment parameters.
        clatter = Clatter(objects=clatter_objects,
                          environment=ClatterObject(impact_material=ImpactMaterial.metal,
                                                    size=4,
                                                    amp=0.5,
                                                    resonance=0.4,
                                                    fake_mass=100))
        # Add a benchmarker.
        benchmark = Benchmark()
        # Add the add-ons.
        self.add_ons.extend([benchmark, camera, audio, clatter])
        # Send the commands.
        self.communicate(commands)
        # Start the benchmark.
        benchmark.start()
        # Let the marbles fall.
        for i in range(50):
            self.communicate([])
        benchmark.stop()
        # Return the longest frame (we assume this is the one with all of the impacts).
        return max(benchmark.times[1:])

    def run(self) -> float:
        times = 0
        num_trials = 10
        for i in range(num_trials):
            times += self.trial()
        self.communicate({"$type": "terminate"})
        return times / num_trials


if __name__ == "__main__":
    c = ClatterBenchmark()
    t = c.run()
    print(t)
