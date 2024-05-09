from argparse import ArgumentParser
from pathlib import Path
from typing import List
from tdw_dev.affordance_points_creator import AffordancePointsCreator


parser = ArgumentParser()
parser.add_argument("input",
                    type=str,
                    help="Either the name of a model, or a path to a .txt file. "
                         "If it is a file path, the file is a list of model names separated by \\n.")
parser.add_argument("--library",
                    type=str,
                    default="models_core.json",
                    help="The model library. If this is models_core.json, models_full.json will also be updated.")
parser.add_argument("--screen_width",
                    type=int,
                    default=1024,
                    help="The screen width in pixels.")
parser.add_argument("--screen_height",
                    type=int,
                    default=1024,
                    help="The screen height in pixels.")
parser.add_argument("--no_launch_build",
                    action="store_true",
                    help="If included, this is equivalent to launch_build=False")
parser.add_argument("--min_point_distance",
                    type=float,
                    default=0.025,
                    help="The minimum distance between affordance points. "
                         "This prevents densely-packed affordance points that are at nearly the same position.")
parser.add_argument("--rotate_speed",
                    type=float,
                    default=3,
                    help="The camera rotation speed in degrees per `communicate()` call.")
parser.add_argument("--move_speed",
                    type=float,
                    default=0.1,
                    help="The camera movement (zoom) speed in meters per `communicate()` call.")
parser.add_argument("--eraser_radius",
                    type=float,
                    default=0.025,
                    help="The radius of the eraser when right-clicking to remove affordance points.")
args = parser.parse_args()
# Try to read a file.
path = Path(args.input)
model_names: List[str]
if path.exists():
    model_names = path.read_text(encoding="utf-8").split("\n")
    model_names = [m.strip() for m in model_names]
else:
    model_names = [args.input]
# Launch the controller.
c = AffordancePointsCreator(screen_width=args.screen_width,
                            screen_height=args.screen_height,
                            min_point_distance=args.min_point_distance,
                            rotate_speed=args.rotate_speed,
                            move_speed=args.move_speed,
                            eraser_radius=args.eraser_radius,
                            launch_build=not args.no_launch_build)
# Process each model.
for model_name in model_names:
    c.run(model_name=model_name,
          library_name=args.library)
# End the simulation.
c.communicate({"$type": "terminate"})
