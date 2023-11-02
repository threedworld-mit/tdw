from typing import List
from tdw.add_ons.ui import UI


class LoadingScreen(UI):
    """
    Add a loading screen.
    """

    def __init__(self, canvas_id: int = 0):
        """
        :param canvas_id: The ID of the UI canvas.
        """

        super().__init__(canvas_id=canvas_id)
        # These IDs will be set when the loading screen is added.
        self._background_id: int = 0
        self._text_id: int = 0
        self._added_loading_screen: bool = False

    def get_add_loading_screen(self, text: str = "Loading...", text_size: int = 64) -> List[dict]:
        """
        This function returns a list of commands that will add a loading screen to the scene.

        THIS FUNCTION DOES NOT AUTOMATICALLY SEND THESE COMMANDS. This is unlike nearly all other add-ons!

        The reason is: Add-ons inject their commands at the end of a list of commands being sent to `communicate(commands)`.

        The loading screen should nearly always be added prior to anything else.

        So, to use this function properly: Add the returned list to your initialization commands, followed by every other setup command.

        The loading screen will be automatically removed when this add-on finishes initialization.

        :param text: The loading message text.
        :param text_size: The font size of the loading message text.

        :return: A list of commands.
        """

        # Add the canvas. We need to do this here because this function can, and should, be called before this add-on initializes.
        commands = [{"$type": "add_ui_canvas",
                     "canvas_id": self._canvas_id}]
        self._background_id = self.add_image(self._get_image(color=(0, 0, 0), size={"x": 16, "y": 16}),
                                             position={"x": 0, "y": 0},
                                             size={"x": 16, "y": 16},
                                             rgba=False,
                                             scale_factor={"x": 2000, "y": 2000})
        self._text_id = self.add_text(text=text,
                                      font_size=text_size,
                                      position={"x": 0, "y": 0})
        commands.extend(self.commands[:])
        self.commands.clear()
        self._added_loading_screen = True
        return commands

    def get_initialization_commands(self) -> List[dict]:
        commands = super().get_initialization_commands()
        # Destroy the loading screen, assuming that we created one.
        if self._added_loading_screen:
            self.destroy(self._background_id)
            self.destroy(self._text_id)
        commands.extend(self.commands[:])
        self.commands.clear()
        return commands
