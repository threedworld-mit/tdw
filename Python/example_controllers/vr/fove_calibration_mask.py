from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.fove_leap_motion import FoveLeapMotion
from tdw.add_ons.ui import UI
from tdw.output_data import OutputData, Fove
from tdw.add_ons.object_manager import ObjectManager
from tdw.vr_data.fove.calibration_state import CalibrationState
from tdw.vr_data.fove.eye import Eye
from tdw.vr_data.fove.eye_state import EyeState
import time
from io import BytesIO
from PIL import Image, ImageDraw

"""
Fove eye/hand calibration protocol.
"""
scene_initialized = False
table_id = Controller.get_unique_id()
table_set_ids = []

c = Controller(launch_build=False)
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(Controller.get_add_physics_object(model_name="small_table_green_marble",
                                                  object_id=table_id,
                                                  position={"x": 0, "y": 0, "z": 0},
                                                  scale_factor={"x": 1.0, "y": 1.0, "z": 0.75},
                                                  kinematic=True))
commands.append({"$type": "hide_object","id": table_id})
table_set_ids.append(table_id)
object_id=Controller.get_unique_id()
commands.extend(Controller.get_add_physics_object(model_name="cube",
                                                  object_id=object_id,
                                                  position={"x": 0, "y": 1, "z": -0.2},
                                                  scale_mass=False,
                                                  scale_factor={"x": 0.05, "y": 0.05, "z": 0.05},
                                                  default_physics_values=False,
                                                  mass=1,
                                                  library="models_flex.json"))
commands.append({"$type": "hide_object","id": object_id})
table_set_ids.append(object_id)
object_id=Controller.get_unique_id()
commands.extend(Controller.get_add_physics_object(model_name="baseball",
                                                  object_id=object_id,
                                                  position={"x": -0.044, "y": 1, "z": 0.0360},
                                                  scale_mass=False,
                                                  scale_factor={"x": 1, "y": 1, "z": 1},
                                                  default_physics_values=False,
                                                  mass=1,
                                                  library="models_full.json"))
commands.append({"$type": "hide_object","id": object_id})
table_set_ids.append(object_id)
object_id=Controller.get_unique_id()
commands.extend(Controller.get_add_physics_object(model_name="b03_cocacola_can_cage",
                                                  object_id=object_id,
                                                  position={"x": 0.119, "y": 1, "z": 0.176},
                                                  scale_mass=False,
                                                  scale_factor={"x": 1.35, "y": 1.35, "z": 1.35},
                                                  default_physics_values=False,
                                                  mass=1,
                                                  library="models_full.json"))
commands.append({"$type": "hide_object","id": object_id})
table_set_ids.append(object_id)
object_id=Controller.get_unique_id()
commands.extend(Controller.get_add_physics_object(model_name="vase_02",
                                                  object_id=object_id,
                                                  position={"x": -0.211, "y": 1, "z": 0.1489},
                                                  scale_mass=False,
                                                  scale_factor={"x": 0.85, "y": 0.85, "z": 0.85},
                                                  default_physics_values=False,
                                                  mass=1,
                                                  library="models_core.json"))
commands.append({"$type": "hide_object","id": object_id})
table_set_ids.append(object_id)
object_id=Controller.get_unique_id()
commands.extend(Controller.get_add_physics_object(model_name="coffeemug",
                                                  object_id=object_id,
                                                  position={"x": 0.2, "y": 1, "z": -0.15},
                                                  scale_mass=False,
                                                  scale_factor={"x": 1, "y": 1, "z": 1},
                                                  default_physics_values=False,
                                                  mass=1,
                                                  library="models_core.json"))
commands.append({"$type": "hide_object","id": object_id})
table_set_ids.append(object_id)
object_id=Controller.get_unique_id()
commands.extend(Controller.get_add_physics_object(model_name="mouse_02_vray",
                                                  object_id=object_id,
                                                  position={"x": 0.344, "y": 1, "z": 0.0420},
                                                  scale_mass=False,
                                                  scale_factor={"x": 1, "y": 1, "z": 1},
                                                  default_physics_values=False,
                                                  mass=1,
                                                  library="models_core.json"))
commands.append({"$type": "hide_object","id": object_id})
table_set_ids.append(object_id)
object_id=Controller.get_unique_id()
commands.extend(Controller.get_add_physics_object(model_name="rh10",
                                                  object_id=object_id,
                                                  position={"x": -0.3, "y": 1, "z": -0.15},
                                                  scale_mass=False,
                                                  scale_factor={"x": 0.2, "y": 0.2, "z": 0.2},
                                                  default_physics_values=False,
                                                  mass=1,
                                                  library="models_core.json"))
commands.append({"$type": "hide_object","id": object_id})
table_set_ids.append(object_id)
fove = FoveLeapMotion(use_right_hand=True,
                      position={"x": 0, "y": 1.0, "z": 0},
                      rotation=180.0,
                      time_step=0.01,
                      allow_headset_movement=False,
                      allow_headset_rotation=True,
                      calibration_data_path="D:\\eye_hand_data\\eye_hand_data_",
                      timestamp=True)
c.add_ons.append(fove)
om = ObjectManager()
c.add_ons.append(om)
ui = UI()
c.add_ons.append(ui)
ui.attach_canvas_to_vr_rig(plane_distance=0.12)
screen_size = 512
commands.append({"$type": "set_screen_size",
                 "width": screen_size,
                 "height": screen_size})
c.communicate(commands)

while not fove.done:
    # Test if calibration done.
    if fove.calibration_state == CalibrationState.running and not scene_initialized:
        commands = []
        for i in range(len(table_set_ids) - 1):
            commands.append({"$type": "show_object","id": table_set_ids[i]})
        fove.initialize_scene()
        commands.append({"$type": "teleport_vr_rig", "position": {"x": 0, "y": 1.2, "z": 0.35}})
        scene_initialized = True
        # Create the background UI image.
        bg_size = screen_size * 4
        base_id = ui.add_image(image=Image.new(mode="RGBA", size=(bg_size, bg_size), color=(0, 0, 0, 255)),
                               position={"x": 0, "y": 0},
                               size={"x": bg_size, "y": bg_size})

        # Create the cutout image.
        diameter = 256
        mask = Image.new(mode="RGBA", size=(diameter, diameter), color=(0, 0, 0, 0))
        # Draw a circle.
        draw = ImageDraw.Draw(mask)
        draw.ellipse([(0, 0), (diameter, diameter)], fill=(255, 255, 255, 255))
        x = 0
        y = 0
        # Add the cutout.
        cutout_id = ui.add_cutout(image=mask, position={"x": x, "y": y}, size={"x": diameter, "y": diameter}, base_id=base_id)
        c.communicate([])
        c.communicate(commands)

    resp=c.communicate([])
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
