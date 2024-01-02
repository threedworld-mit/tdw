# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.global_boolean_command import GlobalBooleanCommand


class SetNetworkLogging(GlobalBooleanCommand):
    """
    If True, the build will log every message received from the controller and will log every command that is executed. Initial value = False
    """

    def __init__(self, value: bool):
        """
        :param value: Boolean value.
        """

        super().__init__(value=value)

