from secrets import token_urlsafe
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, AvatarSimpleBody, AvatarNonKinematic, AvatarKinematic, AvatarSegmentationColor

"""
Test the output data of each type of avatar.
"""

if __name__ == "__main__":
    avatar_types = ["A_Simple_Body",
                    "A_Img_Caps_Kinematic"]
    c = Controller()
    avatars = dict()

    cmds = [TDWUtils.create_empty_room(12, 12)]
    # Create each avatar.
    for avatar_type in avatar_types:
        avatar_id = token_urlsafe(3)
        avatars.update({avatar_id: avatar_type})
        cmds.append({"$type": "create_avatar", "id": avatar_id, "type": avatar_type})
    # Get segmentation color data.
    cmds.append({"$type": "send_avatar_segmentation_colors",
                 "frequency": "once"})
    resp = c.communicate(cmds)

    for r in resp[:-1]:
        print(OutputData.get_data_type_id(r), r)

    assert len(resp) == len(avatar_types) + 1

    print("SEGMENTATION COLORS\n")

    for r in resp[:-1]:
        if r == b'':
            continue
        r_id = OutputData.get_data_type_id(r)
        if r_id == 'avsc':
            print("Avatar segmentation color")
            sc = AvatarSegmentationColor(r)
            a_id = sc.get_id()
            print(a_id)
            print(avatars[a_id])
            print(sc.get_segmentation_color())
        print("\n")

    # Receive avatar data.
    resp = c.communicate({"$type": "send_avatars", "frequency": "once"})

    assert len(resp) == len(avatar_types) + 1

    print("AVATAR DATA\n")

    # Parse each type of avatar data.
    for r in resp[:-1]:
        r_id = OutputData.get_data_type_id(r)
        if r_id == 'avnk':
            print("Non-Kinematic Avatar")
            a = AvatarNonKinematic(r)
            print(a.get_avatar_id())
            print(a.get_position())
            print(a.get_rotation())
            print(a.get_forward())
            print(a.get_velocity())
            print(a.get_angular_velocity())
            print(a.get_sleeping())
            print(a.get_mass())
        elif r_id == 'avki':
            print("Kinematic Avatar")
            a = AvatarKinematic(r)
            print(a.get_avatar_id())
            print(a.get_position())
            print(a.get_rotation())
            print(a.get_forward())
        elif r_id == 'avsb':
            print("Simple Body Avatar")
            a = AvatarSimpleBody(r)
            print(a.get_avatar_id())
            print(a.get_position())
            print(a.get_rotation())
            print(a.get_forward())
            print(a.get_velocity())
            print(a.get_angular_velocity())
            print(a.get_sleeping())
            print(a.get_mass())
            print(a.get_visible_body())
        else:
            raise Exception(f"Unexpected avatar type {r_id}")
        print("\n")
    c.communicate({"$type": "terminate"})
