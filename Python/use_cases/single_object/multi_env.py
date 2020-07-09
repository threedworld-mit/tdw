from single_object import SingleObject
from pathlib import Path
from argparse import ArgumentParser

"""
Generate a dataset with multiple environments.
"""

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--library",
                        type=str,
                        default="models_core.json",
                        help="The filename of the model library.")
    parser.add_argument("--dir", type=str, help="The full path of the output directory.")
    args = parser.parse_args()
    scenes = ["building_site",
              "lava_field",
              "iceland_beach",
              "ruin",
              "dead_grotto",
              "abandoned_factory"]
    train = 1300000 / len(scenes)
    val = 50000 / len(scenes)
    s = SingleObject(new=True,
                     clamp_rotation=True,
                     less_dark=True,
                     hdri=True,
                     no_overwrite=True,
                     max_height=0.5,
                     grayscale_threshold=0.55,
                     train=train,
                     val=val,
                     do_zip=False,
                     library=args.library)

    # Generate a "partial" dataset per scene.
    for scene, i in zip(scenes, range(len(scenes))):
        print(f"{scene}\t{i + 1}/{len(scenes)}")
        s.run(args.dir, scene_name=scene)
    # Terminate the build.
    s.communicate({"$type": "terminate"})

    # Zip.
    SingleObject.zip_images(Path(args.dir))
