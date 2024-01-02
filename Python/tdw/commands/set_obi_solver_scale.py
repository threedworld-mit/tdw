# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.obi_command import ObiCommand


class SetObiSolverScale(ObiCommand):
    """
    Set an Obi solver's scale. This will uniformly scale the physical size of the simulation, without affecting its behavior.
    """

    def __init__(self, solver_id: int = 0, scale_factor: float = 1.0):
        """
        :param solver_id: The solver ID.
        :param scale_factor: The factor to scale XYZ by.
        """

        super().__init__()
        """:field
        The solver ID.
        """
        self.solver_id: int = solver_id
        """:field
        The factor to scale XYZ by.
        """
        self.scale_factor: float = scale_factor
