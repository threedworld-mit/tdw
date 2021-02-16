from argparse import ArgumentParser
from time import time
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils


"""
Use this script to benchmark TDW.
"""


class Benchmarker(Controller):
    def __init__(self, port: int = 1071, check_version: bool = True, launch_build=False):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)

    def run(self, boxes=False, hi_res=False, passes="none", png=False, transforms=False, rigidbodies=False,
            collisions=False, bounds=False, size=256, junk=0, images=False, id_colors=False, id_grayscale=False,
            collision_enter=True, collision_exit=True, collision_stay=True, env_collisions=False,
            row="", return_row=True):

        # Set the render quality.
        # Create the room.
        commands = [{"$type": "set_render_quality",
                     "render_quality": 5 if hi_res else 0},
                    {"$type": "set_post_process",
                     "value": hi_res},
                    {"$type": "set_screen_size",
                     "width": size,
                     "height": size},
                    {"$type": "set_img_pass_encoding",
                     "value": png},
                    TDWUtils.create_empty_room(30, 30)]

        if boxes:
            y = 0.5
            # Create 100 boxes.
            object_ids = []
            for i in range(100):
                commands.append({"$type": "load_primitive_from_resources",
                                 "primitive_type": "Cube",
                                 "id": i,
                                 "position": {"x": 0, "y": y, "z": 0},
                                 "orientation": {"x": 0, "y": 0, "z": 0}})
                object_ids.append(i)
                y += 1.5

        # Send objects data.
        transforms = "always" if transforms else "never"
        rigidbodies = "always" if rigidbodies else "never"
        bounds = "always" if bounds else "never"
        commands.extend([{"$type": "send_transforms",
                          "frequency": transforms},
                         {"$type": "send_rigidbodies",
                          "frequency": rigidbodies},
                         {"$type": "send_bounds",
                          "frequency": bounds}
                         ])
        if collisions:
            collision_types = ["obj"]
            # Listen for environment collisions, too.
            if env_collisions:
                collision_types.append("env")
            commands.append({"$type": "send_collisions",
                             "enter": collision_enter,
                             "stay": collision_stay,
                             "exit": collision_exit,
                             "collision_types": collision_types})

        if junk > 0:
            commands.append({"$type": "send_junk",
                             "frequency": "always",
                             "length": junk})

        if images:
            # Create the avatar.
            commands.extend([{"$type": "create_avatar",
                             "id": "a",
                              "type": "A_Img_Caps_Kinematic"},
                             {"$type": "teleport_avatar_to",
                              "position": {"x": 0, "y": 1.5, "z": -2}}])

            # Enable the _img pass mask.
            if passes == '_img':
                pass_masks = ['_img']
            elif passes == '_id':
                pass_masks = ['_id']
            elif passes == '_img_id':
                pass_masks = ["_img", "_id"]
            else:
                pass_masks = []
            commands.append({"$type": "set_pass_masks",
                             "pass_masks": pass_masks})

            if passes != "none":
                # Start image capture.
                commands.append({"$type": "send_images",
                                 "frequency": "always"})
        if id_colors:
            commands.append({"$type": "send_id_pass_segmentation_colors",
                             "frequency": "always"})
        if id_grayscale:
            commands.append({"$type": "send_id_pass_grayscale",
                             "frequency": "always"})

        # Send all of the init commands.
        self.communicate(commands)

        # Run the trials.
        num_trials = 0
        t0 = time()
        while num_trials < 50000:
            if num_trials % 200 == 0:
                print('num_trials=%d' % num_trials)
            self.communicate([])
            num_trials += 1

        # Calculate the FPS.
        fps = (num_trials / (time() - t0))

        if return_row:
            return "| `" + row + "` | " + str(round(fps)) + " |"
        else:
            return round(fps)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--hi_res', action='store_true')
    parser.add_argument('--images', action='store_true')
    parser.add_argument('--boxes', action='store_true')
    parser.add_argument('--transforms', action='store_true')
    parser.add_argument('--rigidbodies', action='store_true')
    parser.add_argument('--bounds', action='store_true')
    parser.add_argument('--junk', type=int, default=0)
    parser.add_argument('--collisions', action='store_true')
    parser.add_argument('--lots_of_junk', action='store_true')
    parser.add_argument('--png', action='store_true')
    parser.add_argument('--passes', default='_img', choices=['_img', '_img_id', '_id', 'none'])
    parser.add_argument('--size', type=int, default=256)
    parser.add_argument('--id_colors', action='store_true')
    parser.add_argument('--id_grayscale', action='store_true')
    parser.add_argument('--collision_enter', type=lambda x: (str(x).lower() == 'true'), default=True)
    parser.add_argument('--collision_exit', type=lambda x: (str(x).lower() == 'true'), default=True),
    parser.add_argument('--collision_stay', type=lambda x: (str(x).lower() == 'true'), default=True)
    parser.add_argument('--env_collisions', action='store_true')
    args = parser.parse_args()

    # Run the benchmark.
    b = Benchmarker(launch_build=True, check_version=False)
    b.start()
    fps = b.run(boxes=args.boxes, hi_res=args.hi_res, passes=args.passes, png=args.png, transforms=args.transforms,
                rigidbodies=args.rigidbodies, collisions=args.collisions, bounds=args.bounds, size=args.size,
                junk=args.junk, images=args.images, id_colors=args.id_colors, id_grayscale=args.id_grayscale,
                collision_enter=args.collision_enter, collision_stay=args.collision_stay, collision_exit=args.collision_exit,
                env_collisions=args.env_collisions is not None, return_row=False)
    print(round(fps))
