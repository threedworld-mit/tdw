from typing import List
from tdw.add_ons.ui import UI


class LoadingScreen(UI):
    """
    Add a loading screen. For this to work correctly, it should always be the *last* element of `c.add_ons`.
    The loading screen will always appear before anything else.
    But if the add-on is last in `c.add_ons` it will be removed after all other initialization commands.
    """

    def __init__(self, canvas_id: int = 0, text: str = "Loading...", text_size: int = 64):
        """
        :param canvas_id: The ID of the UI canvas.
        :param text: The loading message text.
        :param text_size: The font size of the loading message text.
        """

        super().__init__(canvas_id=canvas_id)
        self._text: str = text
        self._text_size: int = text_size
        # These IDs will be set when the loading screen is added.
        self._background_id: int = 0
        self._text_id: int = 0

    def get_early_initialization_commands(self) -> List[dict]:
        # Add the canvas. We need to do this here because this function can, and should, be called before this add-on initializes.
        commands = [{"$type": "add_ui_canvas",
                     "canvas_id": self._canvas_id}]
        # Add the background and text.
        self._background_id = self.add_image(self._get_image(color=(0, 0, 0), size={"x": 16, "y": 16}),
                                             position={"x": 0, "y": 0},
                                             size={"x": 16, "y": 16},
                                             rgba=False,
                                             scale_factor={"x": 2000, "y": 2000})
        self._text_id = self.add_text(text=self._text,
                                      font_size=self._text_size,
                                      position={"x": 0, "y": 0})
        # The previous two calls added commands to self.commands, so include them here and clear self.commands.
        commands.extend(self.commands[:])
        self.commands.clear()
        return commands

    def get_initialization_commands(self) -> List[dict]:
        commands = super().get_initialization_commands()
        # Destroy the loading screen, assuming that we created one.
        self.destroy(self._background_id)
        self.destroy(self._text_id)
        commands.extend(self.commands[:])
        self.commands.clear()
        return commands
