from argparse import ArgumentParser
from tdw.controller import Controller


"""
A tiny controller to add a single object to an empty environment.
This is mostly meant for debugging.

Usage:

python3 add_object.py <model name>
<Run TDW>
"""


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("model_name", type=str, help="The model name.")
    args = parser.parse_args()
    print("Launch the build in Unity Editor.")

    c = Controller(launch_build=False)
    c.communicate([{"$type": "create_empty_environment"},
                   c.get_add_object(model_name=args.model_name,
                                    library="models_full.json",
                                    object_id=c.get_unique_id())])
