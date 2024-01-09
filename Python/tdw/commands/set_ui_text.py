# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.set_ui_element_command import SetUiElementCommand


class SetUiText(SetUiElementCommand):
    """
    Set the text of a Text object that is already on the screen.
    """

    def __init__(self, id: int, text: str, canvas_id: int = 0):
        """
        :param id: The unique ID of the UI element.
        :param text: The new text.
        :param canvas_id: The unique ID of the UI canvas.
        """

        super().__init__(id=id, canvas_id=canvas_id)
        """:field
        The new text.
        """
        self.text: str = text