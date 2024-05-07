from typing import Dict
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.fove_leap_motion import FoveLeapMotion
from tdw.add_ons.ui import UI
from tdw.replicant.arm import Arm
from tdw.output_data import OutputData, Fove
from tdw.add_ons.object_manager import ObjectManager
from tdw.vr_data.fove.calibration_state import CalibrationState
from tdw.vr_data.fove.eye import Eye
from tdw.vr_data.fove.eye_state import EyeState
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
import time
from io import BytesIO
from PIL import Image, ImageDraw


"""
Fove eye/hand calibration protocol.
"""


def add_and_hide_object(model_name: str, position: Dict[str, float], scale_factor: Dict[str, float], kinematic: bool,
                        library: str = "models_core.json"):
    object_id = Controller.get_unique_id()
    # Add the object.
    commands.extend(Controller.get_add_physics_object(model_name=model_name,
                                                      library=library,
                                                      object_id=object_id,
                                                      position=position,
                                                      scale_factor=scale_factor,
                                                      kinematic=kinematic,
                                                      default_physics_values=not kinematic,
                                                      mass=1,
                                                      scale_mass=False))
    # Hide the object.
    commands.append({"$type": "hide_object",
                     "id": table_id})
    # Remember the object ID.
    table_set_ids.append(object_id)

scene_initialized = False
table_id = Controller.get_unique_id()
table_set_ids = []

c = Controller()
commands = [TDWUtils.create_empty_room(12, 12)]
add_and_hide_object(model_name="small_table_green_marble",
                    position={"x": 0, "y": 0, "z": 0},
                    scale_factor={"x": 1.0, "y": 1.0, "z": 0.75},
                    kinematic=True)
add_and_hide_object(model_name="cube",
                    library="models_flex.json",
                    position={"x": 0, "y": 1, "z": -0.2},
                    scale_factor={"x": 0.05, "y": 0.05, "z": 0.05},
                    kinematic=False)
add_and_hide_object(model_name="baseball",
                    position={"x": -0.044, "y": 1, "z": 0.0360},
                    scale_factor={"x": 1, "y": 1, "z": 1},
                    kinematic=False)
add_and_hide_object(model_name="b03_cocacola_can_cage",
                    position={"x": 0.119, "y": 1, "z": 0.176},
                    scale_factor={"x": 1.35, "y": 1.35, "z": 1.35},
                    kinematic=False)
add_and_hide_object(model_name="vase_02",
                    position={"x": -0.211, "y": 1, "z": 0.1489},
                    scale_factor={"x": 0.85, "y": 0.85, "z": 0.85},
                    kinematic=False)
add_and_hide_object(model_name="coffeemug",
                    position={"x": 0.2, "y": 1, "z": -0.15},
                    scale_factor={"x": 1, "y": 1, "z": 1},
                    kinematic=False)
add_and_hide_object(model_name="mouse_02_vray",
                    position={"x": 0.344, "y": 1, "z": 0.0420},
                    scale_factor={"x": 1, "y": 1, "z": 1},
                    kinematic=False)
add_and_hide_object(model_name="rh10",
                    position={"x": -0.3, "y": 1, "z": -0.15},
                    scale_factor={"x": 0.2, "y": 0.2, "z": 0.2},
                    kinematic=False)
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("fove_scene")
print(f"Calibration data will be saved to: {path}")
fove = FoveLeapMotion(calibration_hand=Arm.left,
                      position={"x": 0, "y": 1.0, "z": 0},
                      rotation=180.0,
                      time_step=0.01,
                      allow_headset_movement=False,
                      allow_headset_rotation=True,
                      calibration_data_path=str(path.resolve()),
                      timestamp=True)
c.add_ons.append(fove)
om = ObjectManager()
c.add_ons.append(om)
ui = UI()
c.add_ons.append(ui)
ui.attach_canvas_to_vr_rig(plane_distance=0.12)
c.communicate(commands)

while not fove.done:
    # Test if calibration done.
    if fove.calibration_state == CalibrationState.running and not scene_initialized:
        commands = []
        for i in range(len(table_set_ids) - 1):
            commands.append({"$type": "show_object",
                             "id": table_set_ids[i]})
        fove.initialize_scene()
        commands.append({"$type": "teleport_vr_rig", "position": {"x": 0, "y": 1.2, "z": 0.35}})
        scene_initialized = True
        # Create the UI image with PIL.
        # The image is larger than the screen size so we can move it around.
        image_size = screen_size * 4
        image = Image.new(mode="RGBA", size=(image_size, image_size), color=(0, 0, 0, 255))
        # Draw a circle on the mask.
        draw = ImageDraw.Draw(image)
        diameter = 384
        d = image_size // 2 - diameter // 2
        draw.ellipse([(d, d), (d + diameter, d + diameter)], fill=(0, 0, 0, 0))
        # Convert the PIL image to bytes.
        with BytesIO() as output:
            image.save(output, "PNG")
            mask = output.getvalue()
        x = 0
        y = 0
        # Add the image.
        mask_id = ui.add_image(image=mask, position={"x": x, "y": y}, size={"x": image_size, "y": image_size}, raycast_target=False)
        c.communicate([])
        c.communicate(commands)

    resp = c.communicate([])
    # Use the appropriate gaze ray based on eye state.
    if scene_initialized:
        if fove.left_eye.state == EyeState.closed and fove.right_eye.state == EyeState.opened:
            curr_object_id = fove.right_eye.gaze_id
        elif fove.right_eye.state == EyeState.closed and fove.left_eye.state == EyeState.opened:
            curr_object_id = fove.left_eye.gaze_id
        else:
            curr_object_id = fove.converged_eyes.gaze_id
        for id in om.transforms:
            # Highlight objects in blue when gaze is on them, skipping the table.
            if (curr_object_id is not None) and (curr_object_id != table_id) and id == curr_object_id:
                c.communicate({"$type": "set_color", "color": {"r": 0, "g": 0, "b": 1.0, "a": 1.0}, "id": curr_object_id})
            # Reset albedo color of all objects except gazed object to normal.
            else:
                c.communicate({"$type": "set_color", "color": {"r": 1.0, "g": 1.0, "b": 1.0, "a": 1.0}, "id": id})

   
c.communicate({"$type": "terminate"})
