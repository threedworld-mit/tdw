from typing import List
from tdw.add_ons.add_on import AddOn


class SetScreenSize(AddOn):
    def __init__(self, width: int, height: int):
        super().__init__()
        self.width: int = width
        self.height: int = height

    def get_initialization_commands(self) -> List[dict]:
        return [{"$type": "set_screen_size",
                 "width": self.width,
                 "height": self.height}]

    def on_send(self, resp: List[bytes]) -> None:
        return

    def set(self, width: int, height: int):
        self.commands.append({"$type": "set_screen_size",
                              "width": width,
                              "height": height})
