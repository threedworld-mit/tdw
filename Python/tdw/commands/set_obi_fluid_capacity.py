# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.obi_fluid_command import ObiFluidCommand


class SetObiFluidCapacity(ObiFluidCommand):
    """
    Set a fluid emitter's particle capacity.
    """

    def __init__(self, id: int, capacity: int):
        """
        :param id: The unique object ID.
        :param capacity: The maximum amount of emitted particles.
        """

        super().__init__(id=id)
        """:field
        The maximum amount of emitted particles.
        """
        self.capacity: int = capacity