from subprocess import call, check_output
import os
from shutil import copyfile
from distutils import dir_util
from pathlib import Path
from argparse import ArgumentParser
from platform import system
from pkg_resources import get_distribution, DistributionNotFound
from sys import argv


if __name__ == "__main__":
    spec = "controller.spec"
    root_dir = Path.home().joinpath("tdw_build")
    if not root_dir.exists():
        root_dir.mkdir()
    # Remove an existing frozen controller.
    output_dir = root_dir.joinpath("tdw_controller")
    if output_dir.exists():
        dir_util.remove_tree(str(output_dir.resolve()))
    output_dir.mkdir(parents=True)

    parser = ArgumentParser()
    parser.add_argument("--args", type=str, help='Arguments for the controller when it launches. '
                                                 'These will be stored in a text file. '
                                                 'Encapsulate the arguments in quotes, e.g. "--num_images 100"')
    parser.add_argument("--controller", type=str, default="example_controllers/minimal.py",
                        help="The relative path from this script to your controller. "
                             "Example: example_controllers/minimal.py")
    args = parser.parse_args()
    if args.args is None:
        arguments = '""'
    else:
        arguments = args.args
    controller = Path(args.controller)
    if not controller.exists():
        raise Exception(f"Controller not found: {controller.resolve()}")
    # Write the config text.
    config_text = f"args={arguments}\ncontroller={str(controller.resolve())}"
    root_dir.joinpath("freeze.ini").write_text(config_text, encoding="utf-8")
    p = system()

    # Install PyInstaller.
    try:
        get_distribution("pyinstaller")
    except DistributionNotFound:
        if p == "Windows":
            call(["pip3", "install", "pyinstaller", "--user"])
        else:
            call(["pip3", "install", "pyinstaller"])

    # Create the executable.
    if p == "Linux":
        call(["python3.6", "-m", "PyInstaller", spec, "--onefile"])
    elif p == "Darwin":
        call(["python3.7", "-m", "PyInstaller", spec, "--onefile", "--windowed"])
    else:
        call(["py", "-3", "-m", "PyInstaller", spec, "--onefile"])
    exit()

# Move the executable.
if p == "windows":
    azazel_exe = "AZAZEL.exe"
elif p == "linux":
    azazel_exe = "AZAZEL"
else:
    azazel_exe = "AZAZEL.app"
exe_dest = output_dir.joinpath(azazel_exe)
if exe_dest.exists():
    os.remove(str(exe_dest.resolve()))
os.rename("dist/" + azazel_exe, str(exe_dest.resolve()))

if p != "osx":
    # Create new directories.
    for directory in ["data", "sound", "fonts"]:
        assert os.path.exists(directory)
        dest = str(output_dir.joinpath(directory).resolve())
        # Remove existing directories.
        if os.path.exists(dest):
            rmtree(dest)
        os.makedirs(dest)

    # Copy the data files.
    files = ["sound/cool_nidre.ogg",
             "sound/tokef_loop.mp3",
             "sound/t_bleat1.ogg",
             "sound/z_bleat1.ogg",
             "data/controls.txt",
             "data/leviticus.txt",
             "data/splash.txt",
             "data/wonders.json",
             "data/icon.png"
             ]
    for font in Path("fonts").glob("azazel_*.png"):
        files.append(f"fonts/{font.name}")

    for file in files:
        dest = str(output_dir.joinpath(file).resolve())
        copyfile(file, dest)

# Copy the README file.
readme = "README.html"
readme_dest = str(output_dir.joinpath(readme).resolve())
if os.path.exists(readme_dest):
    os.remove(readme_dest)
copyfile(readme, readme_dest)

# Go to the correct butler executable.
os.chdir(f"itch/butler/{p}")

release_path = Path(f"../../../dist/release/{args.version}")
assert release_path.exists()

for f in release_path.iterdir():
    if f.is_dir():
        if p == "linux":
            exe = "./butler"
        elif p == "windows":
            exe = "./butler.exe"
        else:
            exe = "./butler"
        if not args.dry_run:
            call([exe, "push", str(f.resolve()), f"subalterngames/azazel:{f.stem}", "--userversion", str(args.version)])

