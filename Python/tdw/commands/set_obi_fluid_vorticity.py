# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.obi_fluid_fluid_command import ObiFluidFluidCommand


class SetObiFluidVorticity(ObiFluidFluidCommand):
    """
    Set a fluid's vorticity.
    """

    def __init__(self, id: int, vorticity: float):
        """
        :param id: The unique object ID.
        :param vorticity: Amount of vorticity confinement, it will contribute to maintain vortical details in the fluid. This value should always be between approximately 0 and 0.5.
        """

        super().__init__(id=id)
        """:field
        Amount of vorticity confinement, it will contribute to maintain vortical details in the fluid. This value should always be between approximately 0 and 0.5.
        """
        self.vorticity: float = vorticity
