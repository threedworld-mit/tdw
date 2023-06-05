import numpy as np
from tdw.output_data import ObiParticles


class ObiActor:
    """
    Data for an Obi actor.
    """

    def __init__(self, object_id: int, solver_id: int, object_index: int):
        """
        :param object_id: The object ID.
        :param solver_id: The ID of the object's Obi solver.
        :param object_index: The index of the object in the `ObiParticles` output data.
        """

        """:field
        The object ID.
        """
        self.object_id: int = object_id
        self._solver_id: int = solver_id
        self._object_index: int = object_index
        """:field
        The positions of each particle as a numpy array.
        """
        self.positions: np.ndarray = np.array([], dtype=np.float32)
        """:field
        The velocities of each particle as a numpy array.
        """
        self.velocities: np.ndarray = np.array([], dtype=np.float32)

    def on_communicate(self, obi_particles: ObiParticles) -> None:
        """
        On `communicate()`, update `self.positions` and `self.velocities`.

        :param obi_particles: `ObiParticles` output data.
        """

        # Get the indices of the active particles.
        solver_indices = obi_particles.get_solver_indices(self._object_index)[:obi_particles.get_count(self._object_index)]
        # Get the particle data at the solver index positions.
        # Reshape the array to (n, 4).
        # Delete the 4th column.
        self.positions = np.delete(np.take(obi_particles.get_positions(self._solver_id).reshape(-1, 4),
                                           solver_indices, axis=0).reshape(-1, 4), 3, 1)
        self.velocities = np.delete(np.take(obi_particles.get_velocities(self._solver_id).reshape(-1, 4),
                                            solver_indices, axis=0).reshape(-1, 4), 3, 1)
