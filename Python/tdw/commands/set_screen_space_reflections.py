# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.post_process_command import PostProcessCommand


class SetScreenSpaceReflections(PostProcessCommand):
    """
    Turn ScreenSpaceReflections on or off.
    """

    def __init__(self, enabled: bool = True):
        """
        :param enabled: If true, screen space reflections are enabled.
        """

        super().__init__()
        """:field
        If true, screen space reflections are enabled.
        """
        self.enabled: bool = enabled