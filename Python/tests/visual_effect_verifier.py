from json import dumps
from typing import Dict
import numpy as np
from tqdm import tqdm
from tdw.controller import Controller
from tdw.librarian import VisualEffectLibrarian
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.output_data import Images
from tdw.tdw_utils import TDWUtils
from tdw.backend.paths import ASSET_BUNDLE_VERIFIER_OUTPUT_DIR


flood_positions: Dict[str, Dict[str, float]] = {"fplan1_floor1": {"x": 10.99, "y": -0.099, "z": -2.78},
                                                "fplan1_floor2": {"x": 6.49, "y": -0.099, "z": -2.78},
                                                "fplan1_floor3": {"x": 0.7399, "y": -0.099, "z": -2.78},
                                                "fplan1_floor4": {"x": 0.2399, "y": -0.099, "z": 2.72},
                                                "fplan1_floor5": {"x": -5.76, "y": -0.099, "z": 2.72},
                                                "fplan1_floor6": {"x": -11.26, "y": -0.099, "z": 2.72},
                                                "fplan2_floor1": {"x": 8.933, "y": -0.1, "z": 2.676},
                                                "fplan2_floor2": {"x": 8.933, "y": -0.1, "z": 2.676},
                                                "fplan2_floor3": {"x": 8.933, "y": -0.1, "z": 2.676},
                                                "fplan2_floor4": {"x": 8.933, "y": -0.1, "z": 2.676},
                                                "fplan2_floor5": {"x": 8.933, "y": -0.1, "z": 2.676},
                                                "fplan2_floor6": {"x": 8.933, "y": -0.1, "z": 2.676},
                                                "fplan2_floor7": {"x": 8.933, "y": -0.1, "z": 2.676},
                                                "fplan2_floor8": {"x": 8.933, "y": -0.1, "z": 2.676},
                                                "fplan4_floor1": {"x": 5.15, "y": -0.099, "z": 3.7},
                                                "fplan4_floor2": {"x": 5.15, "y": -0.099, "z": -0.049},
                                                "fplan4_floor3": {"x": 4.15, "y": -0.099, "z": -3.55},
                                                "fplan4_floor4": {"x": -1.35, "y": -0.099, "z": -3.55},
                                                "fplan4_floor5": {"x": -6.1, "y": -0.099, "z": -2.8},
                                                "fplan4_floor6": {"x": -6.1, "y": -0.099, "z": 1.2},
                                                "fplan4_floor7": {"x": -6.1, "y": -0.099, "z": 4.2},
                                                "fplan5_floor1": {"x": 8.391, "y": 0, "z": -2.793},
                                                "fplan5_floor2": {"x": 3.391, "y": 0, "z": -2.793},
                                                "fplan5_floor3": {"x": -2.608, "y": 0, "z": -2.793},
                                                "fplan5_floor4": {"x": -8.358, "y": 0, "z": -2.793},
                                                "fplan5_floor5": {"x": -2.608, "y": 0, "z": 2.706},
                                                "fplan5_floor6": {"x": 3.391, "y": 0, "z": 2.706}}
path = ASSET_BUNDLE_VERIFIER_OUTPUT_DIR.joinpath("visual_effects.json")
print(f"Results will be saved to: {path}")
missing_material_color: np.ndarray = np.array([255, 0, 255])
c = Controller()
c.communicate([{"$type": "set_screen_size",
                "width": 256,
                "height": 256},
               {"$type": "set_render_quality",
                "render_quality": 5},
               {"$type": "set_post_process",
                "value": False},
               {"$type": "set_img_pass_encoding",
                "value": True}])
result = dict()
for library in VisualEffectLibrarian.get_library_filenames():
    lib = VisualEffectLibrarian(library=library)
    result_lib: Dict[str, bool] = dict()
    pbar = tqdm(total=len(lib.records))
    flood = "flood" in library
    for record in lib.records:
        pbar.set_description(record.name)
        c.add_ons.clear()
        camera = ThirdPersonCamera(position={"x": 0, "y": 28.1 if flood else 2.25, "z": 0},
                                   look_at={"x": 0, "y": 0, "z": 0},
                                   avatar_id="a")
        c.add_ons.append(camera)
        if flood:
            position = flood_positions[record.name]
            rotation = {"x": 90, "y": 0, "z": 0}
        else:
            position = TDWUtils.VECTOR3_ZERO
            rotation = TDWUtils.VECTOR3_ZERO
        c.communicate([{"$type": "load_scene",
                        "scene_name": "ProcGenScene"},
                       {"$type": "create_empty_environment"},
                       Controller.get_add_visual_effect(name=record.name, effect_id=0, library=library,
                                                        position=position, rotation=rotation)])
        # Image capture.
        resp = c.communicate([{"$type": "set_pass_masks",
                               "pass_masks": ["_img"],
                               "avatar_id": "a"},
                              {"$type": "send_images"}])
        # Look for pink pixels.
        image = np.array(TDWUtils.get_pil_image(Images(resp[0]), 0))
        ok = True
        for pixel in image:
            if np.array_equal(pixel, missing_material_color):
                ok = False
                break
        result_lib[record.name] = ok
        pbar.update(1)
    result[library] = result_lib
    pbar.close()
path.write_text(dumps(result, indent=2, sort_keys=True))
c.communicate({"$type": "terminate"})
