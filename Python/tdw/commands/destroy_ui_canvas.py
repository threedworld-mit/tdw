# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.ui_command import UiCommand


class DestroyUiCanvas(UiCommand):
    """
    Destroy a UI canvas and all of its UI elements.
    """

    def __init__(self, canvas_id: int = 0):
        """
        :param canvas_id: The unique ID of the UI canvas.
        """

        super().__init__(canvas_id=canvas_id)
