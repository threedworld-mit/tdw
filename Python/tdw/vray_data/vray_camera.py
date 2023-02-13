from pathlib import Path
import re


class VRayCamera:
    """
    Data for a VRay camera.
    """

    def __init__(self, path: Path):
        """
        :param path: The path to the local .vrscene scene file.
        """

        text = path.read_text(encoding="utf-8")
        """:field
        The string of the render view line.
        """
        self.render_view_id_string: str = re.search(r"(RenderView (.*?){)", text).group(1)
        """:field
        The line number of the render view line.
        """
        self.render_view_line_number: int = -1
        """:field
        The line number of the focal length line.
        """
        self.focal_length_line_number: int = -1
        lines = text.split("\n")
        render_view_pattern = re.compile("RenderView")
        camera_physical = re.compile("CameraPhysical")
        for i, line in enumerate(lines):
            if render_view_pattern.search(line):
                # We will want to replace the line following the "RenderView" line, with the transform data.
                self.render_view_line_number = i
            if camera_physical.search(line):
                # We will want to replace the third line following the "CameraPhysical" line, with the TDW focal length.
                self.focal_length_line_number = i + 3
        if self.render_view_line_number < 0:
            raise Exception(f"RenderView not found in {path}")
        if self.focal_length_line_number < 0:
            raise Exception(f"CameraPhysical not found in {path}")
