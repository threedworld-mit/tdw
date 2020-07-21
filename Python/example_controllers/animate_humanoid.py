from tdw.librarian import HumanoidAnimationLibrarian, HumanoidLibrarian
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils


"""
Create a humanoid and play some animations.
"""


class HumanoidAnimation(Controller):
    def run(self):
        # Instantiate the librarians.
        self.humanoid_animation_librarian = HumanoidAnimationLibrarian()
        self.humanoid_librarian = HumanoidLibrarian()
        # Get the records.
        humanoid_record = self.humanoid_librarian.get_record("man_suit")
        wading_record = self.humanoid_animation_librarian.get_record("wading_through_water")
        fencing_record = self.humanoid_animation_librarian.get_record("fencing")

        h_id = 0

        # Load the streamed scene.
        self.load_streamed_scene(scene="tdw_room_2018")

        # Create the avatar.
        self.communicate(TDWUtils.create_avatar(position={"x": -4.42, "y": 1.5, "z": 5.95}, look_at={"x": 0, "y": 1.0, "z": -3}))

        # Make Unity's framerate match that of the animation clip.
        self.communicate({"$type": "set_target_framerate", "framerate": wading_record.framerate})

        self.communicate([{"$type": "add_humanoid",
                           "name": humanoid_record.name,
                           "position": {"x": 0, "y": 0, "z": -4},
                           "url": humanoid_record.get_url(),
                           "id": h_id},
                          {"$type": "add_humanoid_animation",
                           "name": wading_record.name,
                           "url": wading_record.get_url()},
                          {"$type": "play_humanoid_animation",
                           "name": wading_record.name,
                           "id": h_id}])

        # First, play the "wading_through_water" animation, which is looped. We can test for this:
        if wading_record.loop:
            num_loops = 4
        else:
            num_loops = 1

        for i in range(num_loops):
            self.communicate([])
            self.communicate({"$type": "play_humanoid_animation",
                              "name": wading_record.name,
                              "id": h_id})
            frame = 0
            num_frames = wading_record.get_num_frames()
            while frame < num_frames:
                self.communicate([])
                frame += 1

        # Now play the regular, non-looped "fencing" animation
        # Make Unity's framerate match that of the animation clip.
        self.communicate({"$type": "set_target_framerate",
                          "framerate": fencing_record.framerate})

        self.communicate([{"$type": "add_humanoid_animation",
                           "name": fencing_record.name,
                           "url": fencing_record.get_url()},
                          {"$type": "play_humanoid_animation",
                           "name": fencing_record.name,
                           "id": h_id}])
        frame = 0
        num_frames = fencing_record.get_num_frames()
        while frame < num_frames:
            self.communicate([])
            frame += 1


if __name__ == "__main__":
    HumanoidAnimation().run()
