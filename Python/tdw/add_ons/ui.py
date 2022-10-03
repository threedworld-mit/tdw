from io import BytesIO
from base64 import b64encode
from typing import Tuple, List, Dict, Union
from pathlib import Path
from PIL import Image
from tdw.controller import Controller
from tdw.add_ons.add_on import AddOn


class UI(AddOn):
    """
    Manager add-on for UI in TDW.

    ## Parameter types

    All parameters of type `Dict[str, float]` are Vector2, e.g. `{"x": 0, "y": 0}`. There is no `"z"` parameter.

    `"x"` is the horizontal value and `"y"` is the vertical value.

    In some cases, this document will note that Vector2 values must be integers. This is usually because they are adjusting a value that references the actual screen pixels.
    """

    def __init__(self, canvas_id: int = 0):
        """
        :param canvas_id: The ID of the UI canvas.
        """

        super().__init__()
        self._canvas_id: int = canvas_id
        self._ui_ids: List[int] = list()

    def get_initialization_commands(self) -> List[dict]:
        return [{"$type": "add_ui_canvas",
                 "canvas_id": self._canvas_id}]

    def on_send(self, resp: List[bytes]) -> None:
        pass

    def add_text(self, text: str, font_size: int, position: Dict[str, int], anchor: Dict[str, float] = None,
                 pivot: Dict[str, float] = None, color: Dict[str, float] = None, raycast_target: bool = True) -> int:
        """
        Add UI text to the scene.

        :param text: The text.
        :param font_size: The size of the font.
        :param position: The screen (pixel) position as a Vector2. Values must be integers.
        :param anchor: The anchor as a Vector2. Values are floats between 0 and 1. If None, defaults to `{"x": 0.5, "y": 0.5}`.
        :param pivot: The pivot as a Vector2. Values are floats between 0 and 1. If None, defaults to `{"x": 0.5, "y": 0.5}`.
        :param color: The color of the text. If None, defaults to `{"r": 1, "g": 1, "b": 1, "a": 1}`.
        :param raycast_target: If True, raycasts will hit the UI element.

        :return: The ID of the new UI element.
        """

        cmd, ui_id = self._get_add_element(command_type="add_ui_text", anchor=anchor, pivot=pivot, position=position,
                                           color=color, raycast_target=raycast_target)
        cmd.update({"text": text,
                    "font_size": font_size})
        self.commands.append(cmd)
        return ui_id

    def add_image(self, image: Union[str, Path, bytes], position: Dict[str, int], size: Dict[str, int],
                  rgba: bool = True, scale_factor: Dict[str, float] = None, anchor: Dict[str, float] = None,
                  pivot: Dict[str, float] = None, color: Dict[str, float] = None, raycast_target: bool = True) -> int:
        """
        Add a UI image to the scene.

        :param image: The image. If a string or `Path`, this is a filepath. If `bytes`, this is the image byte data.
        :param position: The screen (pixel) position as a Vector2. Values must be integers.
        :param size: The pixel size of the image as a Vector2. Values must be integers and must match the actual image size.
        :param rgba: If True, this is an RGBA image. If False, this is an RGB image.
        :param scale_factor: Scale the UI image by this factor. If None, defaults to {"x": 1, "y": 1}.
        :param anchor: The anchor as a Vector2. Values are floats between 0 and 1. If None, defaults to `{"x": 0.5, "y": 0.5}`.
        :param pivot: The pivot as a Vector2. Values are floats between 0 and 1. If None, defaults to `{"x": 0.5, "y": 0.5}`.
        :param color: The color of the text. If None, defaults to `{"r": 1, "g": 1, "b": 1, "a": 1}`.
        :param raycast_target: If True, raycasts will hit the UI element.

        :return: The ID of the new UI element.
        """

        if isinstance(image, str):
            img = b64encode(Path(image).read_bytes()).decode("utf-8")
        elif isinstance(image, Path):
            img = b64encode(image.read_bytes()).decode("utf-8")
        elif isinstance(image, bytes):
            img = b64encode(image).decode("utf-8")
        else:
            raise Exception(f"Invalid image type: {image.__class__}")
        if scale_factor is None:
            scale_factor = {"x": 1, "y": 1}
        cmd, ui_id = self._get_add_element(command_type="add_ui_image", anchor=anchor, pivot=pivot,
                                           position=position, color=color, raycast_target=raycast_target)
        cmd.update({"image": img,
                    "size": size,
                    "rgba": rgba,
                    "scale_factor": scale_factor})
        self.commands.append(cmd)
        return ui_id

    def set_text(self, ui_id: int, text: str) -> None:
        """
        Set the text of a UI text element that is already in the scene.

        :param ui_id: The ID of the UI text element.
        :param text: The text.
        """

        self.commands.append({"$type": "set_ui_text",
                              "id": ui_id,
                              "canvas_id": self._canvas_id,
                              "text": text})

    def set_size(self, ui_id: int, size: Dict[str, float]) -> None:
        """
        Set the size of a UI element that is already in the scene.

        :param ui_id: The ID of the UI element.
        :param size: The size.
        """

        self.commands.append({"$type": "set_ui_element_size",
                              "id": ui_id,
                              "canvas_id": self._canvas_id,
                              "size": size})

    def attach_canvas_to_avatar(self, avatar_id: str = "a", focus_distance: float = 2.5, plane_distance: float = 0.101) -> None:
        """
        Attach the UI canvas to an avatar. This allows the UI to appear in image output data.

        :param avatar_id: The avatar ID.
        :param focus_distance: The focus distance. If the focus distance is less than the default value (2.5), the UI will appear blurry unless post-processing is disabled.
        :param plane_distance: The distance from the camera to the UI canvas. This should be slightly further than the near clipping plane.
        """

        self.commands.extend([{"$type": "set_focus_distance",
                               "focus_distance": focus_distance},
                              {"$type": "attach_ui_canvas_to_avatar",
                               "avatar_id": avatar_id,
                               "canvas_id": self._canvas_id,
                               "plane_distance": plane_distance}])

    def attach_canvas_to_vr_rig(self, plane_distance: float = 0.25) -> None:
        """
        Attach the UI canvas to a VR rig.

        :param plane_distance: The distance from the camera to the UI canvas.
        """

        self.commands.append({"$type": "attach_ui_canvas_to_vr_rig",
                              "plane_distance": plane_distance})

    def destroy(self, ui_id: int) -> None:
        """
        Destroy a UI element.

        :param ui_id: The ID of the UI element.
        """

        self.commands.append({"$type": "destroy_ui_element",
                              "id": ui_id,
                              "canvas_id": self._canvas_id})

    def destroy_all(self, destroy_canvas: bool = False) -> None:
        """
        Destroy all UI elements.

        :param destroy_canvas: If True, destroy the UI canvas and all of its UI elements. If False, destroy the canvas' UI elements but not the canvas itself.
        """

        if destroy_canvas:
            self.commands.append({"$type": "destroy_ui_canvas",
                                  "canvas_id": self._canvas_id})
        else:
            for ui_id in self._ui_ids:
                self.commands.append({"$type": "destroy_ui_element",
                                      "id": ui_id,
                                      "canvas_id": self._canvas_id})
        self._ui_ids.clear()

    def add_loading_screen(self, text: str = "Loading...", text_size: int = 64) -> Tuple[int, int]:
        """
        A macro for adding a simple load screen. Combines `self.add_image()` (adds a black background) and `self.add_text()` (adds a loading message).

        :param text: The loading message text.
        :param text_size: The font size of the loading message text.

        :return: Tuple: The ID of the background image, the ID of the text.
        """

        # Add an empty black image. Source: https://stackoverflow.com/a/38626806
        with BytesIO() as output:
            Image.new(mode="RGB", size=(16, 16)).save(output, "PNG")
            image = output.getvalue()
        background_id = self.add_image(image,
                                       position={"x": 0, "y": 0},
                                       size={"x": 16, "y": 16},
                                       rgba=False,
                                       scale_factor={"x": 2000, "y": 2000})
        # Add text.
        text_id = self.add_text(text=text,
                                font_size=text_size,
                                position={"x": 0, "y": 0})
        return background_id, text_id

    def _get_add_element(self, command_type: str, position: Dict[str, int], anchor: Tuple[float, float] = None,
                         pivot: Dict[str, float] = None, color: Dict[str, float] = None,
                         raycast_target: bool = True) -> Tuple[dict, int]:
        """
        :param position: The screen (pixel) position as a Vector2. Values must be integers.
        :param anchor: The anchor as a Vector2. Values are floats between 0 and 1. If None, defaults to `{"x": 0.5, "y": 0.5}`.
        :param pivot: The pivot as a Vector2. Values are floats between 0 and 1. If None, defaults to `{"x": 0.5, "y": 0.5}`.
        :param color: The color of the text. If None, defaults to `{"r": 1, "g": 1, "b": 1, "a": 1}`.
        :param raycast_target: If True, raycasts will hit the UI element.

        :return: Tuple: A partial command, the ID of the new UI element.
        """

        if anchor is None:
            anchor = {"x": 0.5, "y": 0.5}
        if pivot is None:
            pivot = {"x": 0.5, "y": 0.5}
        if color is None:
            color = {"r": 1, "g": 1, "b": 1, "a": 1}
        ui_id = Controller.get_unique_id()
        self._ui_ids.append(ui_id)
        return {"$type": command_type,
                "id": ui_id,
                "canvas_id": self._canvas_id,
                "anchor": anchor,
                "pivot": pivot,
                "position": position,
                "color": color,
                "raycast_target": raycast_target}, ui_id
