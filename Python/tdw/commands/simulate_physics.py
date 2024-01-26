# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.global_boolean_command import GlobalBooleanCommand


class SimulatePhysics(GlobalBooleanCommand):
    """
    Toggle whether to simulate physics per list of sent commands (i.e. per frame). If false, the simulation won't step the physics forward. Initial value = True (simulate physics per frame).
    """

    def __init__(self, value: bool):
        """
        :param value: Boolean value.
        """

        super().__init__(value=value)
