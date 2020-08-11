from subprocess import call, check_call
from distutils import dir_util
from pathlib import Path
from argparse import ArgumentParser
from platform import system
from pkg_resources import get_distribution, DistributionNotFound


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
        arguments = ''
    else:
        arguments = args.args
    arguments = arguments.replace('"', '')
    controller = Path(args.controller)
    # Parse ~ as the home directory.
    if str(controller.resolve())[0] == "~":
        controller = Path.home().joinpath(str(controller.resolve())[2:])

    if not controller.exists():
        raise Exception(f"Controller not found: {controller.resolve()}")
    # Write the config text.
    config_text = f"args={arguments}\ncontroller={str(controller.resolve())}"
    output_dir.joinpath("freeze.ini").write_text(config_text, encoding="utf-8")
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
    dist_path = str(output_dir.resolve()).replace("\\", "/")
    if p == "Linux":
        call(["python3", "-m", "PyInstaller", spec, "--onefile", "--distpath", dist_path])
        exe = "tdw_controller"
    elif p == "Darwin":
        call(["python3", "-m", "PyInstaller", spec, "--onefile", "--distpath", dist_path,
              "--add-binary='/System/Library/Frameworks/Tk.framework/Tk':'tk'",
              "--add-binary='/System/Library/Frameworks/Tcl.framework/Tcl':'tcl'"])
        exe = "tdw_controller.app"
    elif p == "Windows":
        q = check_call(["py", "-3", "-m", "PyInstaller", spec, "--onefile", "--distpath", dist_path])
        exe = "tdw_controller.exe"
    else:
        raise Exception(f"Platform not supported: {p}")

    exe_path = output_dir.joinpath(exe)
    assert exe_path.exists()
    print(f"Created: {exe_path.resolve()}")

    # Add a shortcut with args.
    if p == "Windows":
        # Install winshell.
        for m in ["pypiwin32", "winshell"]:
            try:
                get_distribution(m)
            except DistributionNotFound:
                call(["pip3", "install", m, "--user"])
        import winshell

        link_path = str(output_dir.joinpath("tdw_controller.lnk").resolve())
        with winshell.shortcut(link_path) as link:
            link.path = str(exe_path.resolve())
            link.description = "TDW controller executable."
            # Add arguments.
            if arguments != "":
                link.arguments = arguments
    else:
        sh = f"./{str(exe_path.resolve())} {arguments}"
        sh_path = output_dir.joinpath("tdw_controller.sh")
        sh_path.write_text(sh, encoding="utf-8")
        call(["chmod", "+x", str(sh_path.resolve())])
