from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import SegmentationColors


if __name__ == "__main__":
    c = Controller()

    # Create the room.
    commands = [TDWUtils.create_empty_room(30, 30)]

    y = 0
    # Create 100 iron boxes.
    object_ids = []
    for i in range(100):
        commands.append(c.get_add_object("dishwasher_4", position={"x": 0, "y": y, "z": 0}, object_id=i))
        object_ids.append(i)
        y += 0.6

    # Add a simple body avatar.
    commands.extend(TDWUtils.create_avatar(avatar_type="A_Simple_Body"))
    commands.append({"$type": "send_segmentation_colors",
                     "frequency": "once"})
    resp = c.communicate(commands)

    for r in resp[:-1]:
        s = SegmentationColors(r)
        assert s.get_num() == 100
        for i in range(s.get_num()):
            print(f"{s.get_object_id(i)}\t{s.get_object_name(i)}\t{s.get_object_color(i)}")
    c.communicate({"$type": "terminate"})
