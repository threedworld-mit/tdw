# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.command import Command


class SetCursor(Command):
    """
    Set cursor parameters.
    """

    def __init__(self, visible: bool = True, locked: bool = False):
        """
        :param visible: If True, the cursor is visible.
        :param locked: If True, the cursor is locked to the center of the screen.
        """

        super().__init__()
        """:field
        If True, the cursor is visible.
        """
        self.visible: bool = visible
        """:field
        If True, the cursor is locked to the center of the screen.
        """
        self.locked: bool = locked
