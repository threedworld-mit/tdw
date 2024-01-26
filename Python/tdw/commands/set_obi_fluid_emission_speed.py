# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.obi_fluid_command import ObiFluidCommand


class SetObiFluidEmissionSpeed(ObiFluidCommand):
    """
    Set the emission speed of a fluid emitter. Larger values will cause more particles to be emitted.
    """

    def __init__(self, id: int, speed: float = 0):
        """
        :param id: The unique object ID.
        :param speed: The speed of emitted particles in meters per second. Set this to 0 to stop emission.
        """

        super().__init__(id=id)
        """:field
        The speed of emitted particles in meters per second. Set this to 0 to stop emission.
        """
        self.speed: float = speed