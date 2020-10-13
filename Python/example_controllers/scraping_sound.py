import json
from pathlib import Path
from tdw.controller import Controller
from tdw.output_data import OutputData, Rigidbodies
from tdw.tdw_utils import TDWUtils
from tdw.librarian import ModelLibrarian
from tdw.py_impact import CollisionTypesOnFrame, CollisionType, PyImpact
from tdw.py_scrape import PyScrape
import numpy as np
import time



class ScrapeSound(Controller):
    """
    Test controller for scraping sound simulation usin gPyScrape.

    Runs three trials of cube bouncing, with third trial generatung scraping as wel las simpact sound.
    """



    def __init__(self, launch_build: bool = True):

        # The object ID of the table surface.
        self.table_id = self.get_unique_id()

        super().__init__(launch_build=launch_build)

        # Initialize the scene.
        self.start()

        # Create the room and the "surface object".
        commands = [TDWUtils.create_empty_room(30, 30),
                    self.get_add_object("glass_table_round",
                                        position={"x": 0, "y": 0, "z": 0},
                                        object_id=self.table_id,
                                        library="models_core.json"),
                    {"$type": "set_kinematic_state",
                     "id": self.table_id,
                     "is_kinematic": True, 
                    "use_gravity": False},
                    {"$type": "scale_object",
                     "scale_factor": {"x": 6, "y": 1.5, "z": 18},
                     "id": self.table_id},
                    {"$type": "set_color",
                     "color": {"r": 0, "g": 1, "b": 1, "a": 1},
                     "id": self.table_id},
                    {"$type": "set_physic_material",
                     "dynamic_friction": 0.3,
                     "static_friction": 0.2,
                     "bounciness": 0.4,
                     "id": self.table_id}]
        # Create the avatar.
        # Request collision data.
        # Add the dropped object's material.
        commands.extend(TDWUtils.create_avatar(position={"x": 7.3, "y": 1.7, "z": 3.6},
                                               look_at={"x": 0, "y": 1.5, "z": 3.6}))
        commands.extend([{"$type": "set_field_of_view",
                          "field_of_view": 70},
                         {"$type": "set_screen_size", 
                          "width": 1024, 
                          "height": 1024},
                         {"$type": "set_render_quality",
                          "render_quality": 0},
                         {"$type": "add_audio_sensor",
                          "avatar_id": "a"},
                         {"$type": "set_target_framerate", 
                          "framerate": 120},
                         {"$type": "send_collisions",
                          "enter": True,
                          "stay": True,
                          "collision_types": ["obj"]}])
        self.communicate(commands)


    def trial(self, y0: float = 4, a0: float = 60) -> None:
        """
        Drop an object.

        :param y0: Initial y position.
        :param a0: Initial pitch angle.
        :param model_name: The name of the model.
        """

        p = PyImpact(initial_amp=0.5)
        s = PyScrape(max_vel=4.0)

        # Add the object and drop it.
        o_id = self.get_unique_id()
        resp = self.communicate([TDWUtils.create_empty_room(30, 30),
                                 self.get_add_object(model_name="prim_cube",
                                                     position={"x": 0, "y": y0, "z": 0},
                                                     object_id=o_id,
                                                     library="models_special.json"),
                                 {"$type": "rotate_object_by",
                                  "angle": a0,
                                  "id": o_id,
                                  "axis": "pitch",
                                  "is_world": True},
                                 {"$type": "set_physic_material",
                                  "dynamic_friction": 0.3,
                                  "static_friction": 0.2,
                                  "bounciness": 0.5,
                                  "id": o_id},
                                 {"$type": "set_mass",
                                  "mass": 2,
                                  "id": o_id},
                                 {"$type": "apply_force_magnitude_to_object",
                                  "magnitude": 12,
                                  "id": o_id},
                                 {"$type": "send_rigidbodies",
                                  "frequency": "always"},
                                 {"$type": "set_object_collision_detection_mode",
                                  "id": o_id,
                                  "mode": "continuous_dynamic"}])

        for i in range(200):
            # Get all types of collision on this frame.
            # If there was a collision, create a sound.
            ctof = CollisionTypesOnFrame(object_id=o_id, resp=resp)
            coll_type = CollisionType.none
            for collidee_id in ctof.collisions:
                coll_type = ctof.collisions[collidee_id]
            for r in resp[:-1]:
                r_id = OutputData.get_data_type_id(r)
                if r_id == "rigi":
                    rbody = Rigidbodies(r)

            # Test ollision type and generate appropriate sound.
            if coll_type == CollisionType.impact:
                collisions, environment_collision, rigidbodies = PyImpact.get_collisions(resp)
                impact_sound_command = p.get_impact_sound_command(
                    collision=collisions[0],
                    rigidbodies=rigidbodies,
                    target_id=o_id,
                    target_mat="metal",
                    target_amp=0.4,
                    other_id=self.table_id,
                    other_amp=0.5,
                    other_mat="glass",
                    resonance=0.85)
                resp = self.communicate(impact_sound_command)
            elif coll_type == CollisionType.scrape:
                collisions, environment_collision, rigidbodies = PyImpact.get_collisions(resp)
                scrape_sound_command = s.get_scrape_sound_command(
                    p=p, 
                    rbody=rbody,
                    collision=collisions[0],
                    rigidbodies=rigidbodies,
                    target_id=o_id,
                    target_mat="metal",
                    target_amp=0.4,
                    other_id=self.table_id,
                    other_amp=0.5,
                    other_mat="glass",
                    resonance=0.75)
                resp = self.communicate(scrape_sound_command)
            resp = self.communicate([])
        # End the trial.
        # Destroy the dropped object.
        self.communicate([{"$type": "destroy_object",
                           "id": o_id},
                          {"$type": "send_rigidbodies",
                           "frequency": "never"}])


if __name__ == "__main__":
    c = ScrapeSound()
    for dly in range(200):
        c.communicate([])
    c.trial()
    c.trial()
    # Slide a cube.
    c.trial(y0=1.3, a0=0)
    c.communicate({"$type": "terminate"})