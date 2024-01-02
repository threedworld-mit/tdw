# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.ui_command import UiCommand


class AttachUiCanvasToVrRig(UiCommand):
    """
    Attach a UI canvas to the head camera of a VR rig.
    """

    def __init__(self, plane_distance: float = 1, canvas_id: int = 0):
        """
        :param plane_distance: The distance from the camera to the UI canvas.
        :param canvas_id: The unique ID of the UI canvas.
        """

        super().__init__(canvas_id=canvas_id)
        """:field
        The distance from the camera to the UI canvas.
        """
        self.plane_distance: float = plane_distance
