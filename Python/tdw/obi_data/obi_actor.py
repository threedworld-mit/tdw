import numpy as np
from tdw.output_data import ObiParticles


class ObiActor:
    """
    Data for an Obi actor.
    """

    def __init__(self, object_id: int, solver_id: int, object_index: int, start: int, count: int):
        """
        :param object_id: The object ID.
        :param solver_id: The ID of the object's Obi solver.
        :param object_index: The index of the object in the `ObiParticles` output data.
        :param start: The start index of the object's particle data.
        :param count: The number of active particles.
        """

        """:field
        The object ID.
        """
        self.object_id: int = object_id
        self._start: int = start
        self._end: int = self._start + count
        self._solver_id: int = solver_id
        self._object_index: int = object_index
        self._count: int = count
        """:field
        The positions of each particle as a numpy array.
        """
        self.positions: np.array = np.delete(np.zeros(shape=(count * 4), dtype=np.float32).reshape(-1, 4), 3, 1)
        """:field
        The velocities of each particle as a numpy array.
        """
        self.velocities: np.array = self.positions.copy()

    def on_communicate(self, obi_particles: ObiParticles) -> None:
        """
        On `communicate()`, update `self.positions` and `self.velocities`.

        :param obi_particles: `ObiParticles` output data.
        """

        count = obi_particles.get_count(self._object_index)
        # If the number of active particles changed, resize the arrays.
        if count != self._count:
            self._start = obi_particles.get_start(self._object_index)
            self._end = self._start + count
            self.positions = np.delete(np.zeros(shape=(count * 4), dtype=np.float32).reshape(-1, 4), 3, 1)
            self.velocities = self.positions.copy()
            self._count = count
        # Copy the particle data into the arrays.
        np.copyto(dst=self.positions, src=obi_particles.get_positions(self._solver_id)[self._start: self._end])
        np.copyto(dst=self.velocities, src=obi_particles.get_velocities(self._solver_id)[self._start: self._end])
