from typing import List, Dict, Union
from tdw.add_ons.add_on import AddOn
from tdw.output_data import OutputData, ObiParticles
from tdw.obi_data.fluids.fluid import Fluid, FLUIDS
from tdw.obi_data.fluids.granular_fluid import GranularFluid, GRANULAR_FLUIDS
from tdw.obi_data.fluids.emitter_shape import EmitterShape
from tdw.obi_data.obi_actor import ObiActor


class Obi(AddOn):
    def __init__(self, output_data: bool = True):
        """
        :param output_data: If True, receive [`ObiParticles`](../../api/output_data.md#ObiParticles) per frame.
        """

        super().__init__()
        """:field
        A dictionary of actor data. Key = Object ID. Value = [`ObiActor`](../obi_data/obi_actor.md). The particle data is updated if `output_data == True` (see above).
        """
        self.actors: Dict[int, ObiActor] = dict()
        self._output_data: bool = output_data

    def get_initialization_commands(self) -> List[dict]:
        commands = [{"$type": "initialize_obi"}]
        if self._output_data:
            commands.append({"$type": "send_obi_particles",
                             "frequency": "always"})
        return commands

    def on_send(self, resp: List[bytes]) -> None:
        # Parse particle data.
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "obip":
                obi_particles = ObiParticles(resp[i])
                for j in range(obi_particles.get_num_objects()):
                    object_id = obi_particles.get_object_id(j)
                    # Add an actor.
                    if object_id not in self.actors:
                        self.actors[object_id] = ObiActor(object_id=object_id,
                                                          object_index=j,
                                                          solver_id=obi_particles.get_solver_id(j),
                                                          start=obi_particles.get_start(j),
                                                          count=obi_particles.get_count(j))
                # Update the particles.
                for object_id in self.actors:
                    self.actors[object_id].on_communicate(obi_particles=obi_particles)

    def create_fluid(self, object_id: int, fluid: Union[str, Fluid, GranularFluid], shape: EmitterShape,
                     position: Dict[str, float] = None, rotation: Dict[str, float] = None, speed: float = 1,
                     lifespan: float = 4, minimum_pool_size: float = 0.5, solver_id: int = 0,
                     particle_radius_scale: float = 1.7, random_velocity: float = 0) -> None:
        """
        Create a cube-shaped fluid emitter.

        :param object_id: The unique ID of the emitter.
        :param fluid: Either a [`Fluid`](../obi_data/fluid.md), a [`GranularFluid`](../obi_data/granular_fluid.md), the name of a fluid (see `Fluid.FLUIDS`), or the name of a granular fluid (see `GranularFluid.GRANULAR_FLUIDS`).
        :param shape: Either a [`CubeEmitter`](emitter_shape/cube_emitter.md), [`DiskEmitter`](emitter_shape/disk_emitter.md), [`EdgeEmitter`](emitter_shape/edge_emitter.md), or [`SphereEmitter`](emitter_shape/sphere_emitter.md).
        :param position: The position of the emitter object. If None, defaults to (0, 0, 0).
        :param rotation: The rotation of the emitter object, in Euler angles.  If None, defaults to (0, 0, 0).
        :param speed: The speed of emission in meters per second. If 0, there is no emission.
        :param lifespan: The particle lifespan in seconds.
        :param minimum_pool_size: The minimum amount of inactive particles available before the emitter is allowed to resume emission.
        :param solver_id: The ID of the Obi solver.
        :param particle_radius_scale: This scales the size at which particles are drawn.
        :param random_velocity: Random velocity of emitted particles.
        """

        # Set a default position and rotation.
        if position is None:
            position = {"x": 0, "y": 0, "z": 0}
        if rotation is None:
            rotation = {"x": 0, "y": 0, "z": 0}
        # Get the fluid. If it's a string, it's a preset.
        if isinstance(fluid, str):
            if fluid in FLUIDS:
                f = FLUIDS[fluid]
            elif fluid in GRANULAR_FLUIDS:
                f = GRANULAR_FLUIDS[fluid]
            else:
                raise Exception(f"Fluid not found: {fluid}")
        else:
            f = fluid
        self.commands.append({"$type": "create_obi_fluid",
                              "id": object_id,
                              "fluid": f.to_dict(),
                              "shape": shape.to_dict(),
                              "position": position,
                              "rotation": rotation,
                              "lifespan": lifespan,
                              "minimum_pool_size": minimum_pool_size,
                              "solver_id": solver_id,
                              "particle_radius_scale": particle_radius_scale,
                              "random_velocity": random_velocity,
                              "speed": speed})

    def set_fluid_speed(self, object_id: int, speed: float) -> None:
        """
        Set the speed of a fluid emitter. By default, the speed of an emitter is 0 (no fluid emission).

        :param object_id: The ID of the fluid emitter.
        :param speed: The speed in meters per second. Set this to 0 to stop emission.
        """

        self.commands.append({"$type": "set_obi_fluid_emission_speed",
                              "id": object_id,
                              "speed": speed})

    def reset(self):
        self.commands.clear()
        self.initialized = False
        self.actors.clear()
