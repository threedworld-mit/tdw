from typing import List
from tdw.add_ons.ui import UI


class LoadingScreen(UI):
    """
    Add a loading screen. For this to work correctly, it should always be the *last* element of `c.add_ons`.
    The loading screen will always appear before anything else.
    But if the add-on is last in `c.add_ons` it will be removed after all other initialization commands.
    """

    def __init__(self, canvas_id: int = 0, loading_text: str = "Loading...", loading_text_size: int = 64,
                 instructions_text: str = None, instructions_text_size: int = 36):
        """
        :param canvas_id: The ID of the UI canvas.
        :param loading_text: The loading message text.
        :param loading_text_size: The font size of the loading message text.
        :param instructions_text: The instructions text subtitle. Can be None.
        :param instructions_text_size: The size of the instructions text (if there is any).
        """

        super().__init__(canvas_id=canvas_id)

        # These functions append commands to `self.commands`:

        # Add the background.
        self.add_image(self._get_image(color=(0, 0, 0), size={"x": 16, "y": 16}),
                       position={"x": 0, "y": 0},
                       size={"x": 16, "y": 16},
                       rgba=False,
                       scale_factor={"x": 2000, "y": 2000})
        # Add the loading text.
        self.add_text(text=loading_text,
                      font_size=loading_text_size,
                      position={"x": 0, "y": 0})
        # Add the instructions text.
        self.add_text(text=instructions_text,
                      font_size=instructions_text_size,
                      position={"x": 0, "y": 0})

        # Remember the early initialization commands.
        self._early_initialization_commands: List[dict] = self.commands[:]
        self.commands.clear()

    def get_early_initialization_commands(self) -> List[dict]:
        # Add the canvas.
        # We need to do this here because this function can, and should, be called before this add-on initializes.
        commands = [{"$type": "add_ui_canvas",
                     "canvas_id": self._canvas_id}]
        commands.extend(self._early_initialization_commands)
        return commands

    def get_initialization_commands(self) -> List[dict]:
        commands = super().get_initialization_commands()
        # Destroy the loading screen.
        self.destroy_all(destroy_canvas=False)
        commands.extend(self.commands[:])
        self.commands.clear()
        return commands
