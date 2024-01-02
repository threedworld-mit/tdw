# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.post_process_command import PostProcessCommand


class SetAmbientOcclusionIntensity(PostProcessCommand):
    """
    Set the intensity (darkness) of the Ambient Occlusion effect.
    """

    def __init__(self, intensity: float = 0.25):
        """
        :param intensity: The intensity (darkness) of the ambient occlusion.
        """

        super().__init__()
        """:field
        The intensity (darkness) of the ambient occlusion.
        """
        self.intensity: float = intensity
