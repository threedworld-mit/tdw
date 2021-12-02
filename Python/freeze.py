from subprocess import call
from distutils import dir_util
from pathlib import Path
from argparse import ArgumentParser
from platform import system


"""
Freeze your controller into a binary executable.

Documentation: `tdw/Documentation/misc_frontend/freeze.md`
"""


if __name__ == "__main__":
    root_dir = Path.home().joinpath("tdw_build")
    if not root_dir.exists():
        root_dir.mkdir()
    # Remove an existing frozen controller.
    output_dir = root_dir.joinpath("tdw_controller")
    if output_dir.exists():
        dir_util.remove_tree(str(output_dir.resolve()))
    output_dir.mkdir(parents=True)
    parser = ArgumentParser()
    parser.add_argument("--controller", type=str,
                        help="The relative path from this script to your controller.")
    args = parser.parse_args()
    controller = Path(args.controller)
    # Parse ~ as the home directory.
    if str(controller.resolve())[0] == "~":
        controller = Path.home().joinpath(str(controller.resolve())[2:])

    if not controller.exists():
        raise Exception(f"Controller not found: {controller.resolve()}")

    # Write the config file. This is used by controller.spec to point to the correct controller.
    config_text = f"controller={str(controller.resolve())}"
    ini_path = output_dir.joinpath("freeze.ini")
    ini_path.write_text(config_text, encoding="utf-8")
    p = system()

    # Create the executable.
    dist_path = str(output_dir.resolve()).replace("\\", "/")
    spec = "controller.spec"
    if p == "Linux":
        call(["python3", "-m", "PyInstaller", spec, "--onefile", "--distpath", dist_path])
        exe = "tdw_controller"
    elif p == "Darwin":
        call(["python3", "-m", "PyInstaller", spec, "--onefile", "--distpath", dist_path])
        exe = "tdw_controller.app"
    elif p == "Windows":
        call(["py", "-3", "-m", "PyInstaller", spec, "--onefile", "--distpath", dist_path])
        exe = "tdw_controller.exe"
    else:
        raise Exception(f"Platform not supported: {p}")

    exe_path = output_dir.joinpath(exe)
    assert exe_path.exists()
    print(f"Created: {exe_path.resolve()}")

    # Remove the config file.
    ini_path.unlink()
