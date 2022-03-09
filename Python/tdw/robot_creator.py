from typing import List, Dict, Optional, Union
from os import getcwd, chdir, walk, devnull
import re
from platform import system
from pathlib import Path
from subprocess import call
from distutils.file_util import copy_file, move_file
from distutils.dir_util import remove_tree
from tdw.asset_bundle_creator_base import AssetBundleCreatorBase
from tdw.librarian import RobotRecord
from tdw.backend.paths import EDITOR_LOG_PATH
from tdw.backend.platforms import UNITY_TO_SYSTEM


class RobotCreator(AssetBundleCreatorBase):
    """
    Download a .urdf or .xacro file and convert it into an asset bundle that is usable by TDW.
    """

    """:class_var
    The root temporary directory.
    """
    TEMP_ROOT: Path = Path.home().joinpath("robot_creator/temp_robots")

    def __init__(self, quiet: bool = False, display: str = ":0", unity_editor_path: Union[Path, str] = None):
        """
        :param quiet: If true, don't print any messages to console.
        :param display: The display to launch Unity Editor on. Ignored if this isn't Linux.
        :param unity_editor_path: The path to the Unity Editor executable, for example `C:/Program Files/Unity/Hub/Editor/2020.3.24f1/Editor/Unity.exe`. If None, this script will try to find Unity Editor automatically.
        """

        super().__init__(quiet=quiet, display=display, unity_editor_path=unity_editor_path)

    def create_asset_bundles(self, urdf_url: str, required_repo_urls: Dict[str, str] = None,
                             xacro_args: Dict[str, str] = None, immovable: bool = True, up: str = "y",
                             description_infix: str = None, branch: str = None) -> RobotRecord:
        """
        Given the URL of a .urdf file or a .xacro file, create asset bundles of the robot.

        This is a wrapper function for:

        1. `clone_repo()`
        2. `copy_files()`
        3. `urdf_to_prefab()`
        4. `prefab_to_asset_bundles()`

        :param urdf_url: The URL of a .urdf or a .xacro file.
        :param required_repo_urls: A dictionary of description folder names and repo URLs outside of the robot's repo that are required to create the robot. This is only required for .xacro files that reference outside repos. For example, the Sawyer robot requires this to add the gripper: `{"intera_tools_description": "https://github.com/RethinkRobotics/intera_common"}`
        :param xacro_args: Names and values for the `arg` tags in the .xacro file (ignored if this is a .urdf file). For example, the Sawyer robot requires this to add the gripper: `{"electric_gripper": "true"}`
        :param immovable: If True, the base of the robot is immovable.
        :param up: The up direction. Used when importing the robot into Unity. Options: `"y"` or `"z"`. Usually, this should be the default value (`"y"`).
        :param description_infix: The name of the description infix within the .urdf URL, such as `fetch_description`. Only set this if the urdf URL is non-standard; otherwise `RobotCreator` should be able to find this automatically.
        :param branch: The name of the branch of the repo. If None, defaults to `"master"`.

        :return: A `RobotRecord` object. The `urls` field contains the paths to each asset bundle.
        """

        if required_repo_urls is None:
            required_repo_urls = list()

        # Clone the repo.
        repo_paths: Dict[str, Path] = dict()
        local_repo_path = self.clone_repo(url=urdf_url)
        if description_infix is None:
            description_infix = RobotCreator._get_description_infix(url=urdf_url)
        repo_paths[description_infix] = local_repo_path

        # Clone the required repos.
        for description in required_repo_urls:
            required_repo_url = required_repo_urls[description]
            required_local_repo_path = self.clone_repo(url=required_repo_url)
            repo_paths[description] = required_local_repo_path

        # Copy the files, create a .urdf file (if needed), and creator collider objects.
        urdf_path = self.copy_files(urdf_url=urdf_url, local_repo_path=local_repo_path, repo_paths=repo_paths,
                                    xacro_args=xacro_args, branch=branch)

        # Create the prefab.
        prefab = self.urdf_to_prefab(urdf_path=urdf_path, immovable=immovable, up=up)
        name = prefab.name.replace(".prefab", "")

        # Create the asset bundles.
        asset_bundles = self.prefab_to_asset_bundles(name=name)
        temp = dict()
        for k in asset_bundles:
            temp[k] = "file:///" + str(asset_bundles[k].resolve()).replace("\\", "/")
        asset_bundles = temp

        # Create the record.
        return RobotCreator.get_record(name=name, urdf_url=urdf_url, immovable=immovable, asset_bundles=asset_bundles)

    @staticmethod
    def get_record(name: str, urdf_url: str, immovable: bool, asset_bundles: Dict[str, str]) -> RobotRecord:
        """
        :param name: The name of the robot.
        :param urdf_url: The URL to the .urdf or .xacro file.
        :param immovable: If True, the base of the robot is immovable.
        :param asset_bundles: The paths to the asset bundles. See `prefab_to_asset_bundles()`.

        :return: A `RobotRecord` metadata object.
        """

        record_data = {"name": name,
                       "source": RobotCreator._get_repo_url(url=urdf_url),
                       "immovable": immovable,
                       "urls": asset_bundles,
                       "targets": {},
                       "ik": {}}
        return RobotRecord(data=record_data)

    def clone_repo(self, url: str) -> Path:
        """
        Clone a repo to a temporary directory.

        :param url: The URL to the .urdf or .xacro file or the repo.

        :return: The temporary directory.
        """

        if not RobotCreator.TEMP_ROOT.exists():
            RobotCreator.TEMP_ROOT.mkdir(parents=True)

        # This is a .urdf or .xacro file. Parse the repo URL accordingly.
        if url.endswith(".xacro") or url.endswith(".urdf"):
            local_repo_path = RobotCreator._get_local_repo_path(url=url)
            repo_url = RobotCreator._get_repo_url(url=url)
        # This is the base URL of the repo. Parse it accordingly.
        else:
            local_repo_path = RobotCreator.TEMP_ROOT.joinpath(Path(url).name)
            repo_url = url
        if local_repo_path.exists():
            return local_repo_path

        # Change directory.
        cwd = getcwd()
        chdir(str(RobotCreator.TEMP_ROOT.resolve()))
        if not self._quiet:
            print(f"Cloning: {repo_url}")
        # Clone the repo.
        call(["git", "clone", repo_url],
             stderr=open(devnull, "wb"))
        chdir(cwd)
        assert local_repo_path.exists(), f"Can't find: {local_repo_path.resolve()}"
        if not self._quiet:
            print("...Done!")
        return local_repo_path

    def copy_files(self, urdf_url: str, local_repo_path: Path, repo_paths: Dict[str, Path],
                   xacro_args: Dict[str, str] = None, branch: str = None) -> Path:
        """
        Copy and convert files required to create a prefab.

        1. If this is a .xacro file, convert it to a .urdf file.
        2. Copy the .urdf file to the Unity project.
        3. Copy all associated meshes to the .urdf project.

        :param urdf_url: The URL to the remote .urdf or .xacro file.
        :param local_repo_path: The path to the local repo.
        :param repo_paths: A dictionary of required repos (including the one that the .urdf or .xacro is in). Key = The description path infix, e.g. "sawyer_description". Value = The path to the local repo.
        :param xacro_args: Names and values for the `arg` tags in the .xacro file. Can be None for a .urdf or .xacro file and always ignored for a .urdf file.
        :param branch: The name of the branch of the repo. If None, defaults to `"master"`.

        :return: The path to the .urdf file in the Unity project.
        """

        page_url = self._raw_to_page(url=urdf_url)
        if branch is None:
            branch = "master"
        repo_path = re.search(r"(.*)/blob/" + branch + r"/(.*)", page_url).group(2)
        urdf_path = local_repo_path.joinpath(repo_path)
        dst_root = self._project_path.joinpath(f"Assets/robots")
        if not dst_root.exists():
            dst_root.mkdir(parents=True)
        # Convert the .xacro file to a .urdf file.
        if Path(urdf_url).suffix == ".xacro":
            urdf_dst = self.xacro_to_urdf(xacro_path=urdf_path, repo_paths=repo_paths, args=xacro_args)
        # Move the existing .urdf file.
        else:
            assert urdf_path.exists(), f"Not found: {urdf_path.resolve()}"
            # Copy the .urdf file.
            urdf_dst = dst_root.joinpath(Path(urdf_url).name)
            copy_file(src=str(urdf_path.resolve()), dst=str(urdf_dst.resolve()))

        # Read the .urdf file.
        urdf = urdf_dst.read_text(encoding="utf-8")
        # Remove gazebo stuff.
        urdf = re.sub(r"<gazebo reference(.*?)>((.|\n)*?)</gazebo>", "", urdf)
        urdf = re.sub(r"<gazebo>((.|\n)*?)</gazebo>", "", urdf)
        urdf = re.sub(r"<transmission((.|\n)*?)</transmission>", "", urdf)
        urdf = re.sub(r'<xacro:include (.*)gazebo(.*)/>', "", urdf)
        urdf_dst.write_text(urdf, encoding="utf-8")
        # Copy the meshes.
        for m in re.findall(r"filename=\"package://((.*)\.(DAE|dae|stl|STL))\"", urdf):
            mesh_description = m[0].split("/")[0]
            mesh_repo: Optional[Path] = None
            mesh_desc = ""
            for k_desc in repo_paths:
                if mesh_description in k_desc:
                    mesh_repo: Path = repo_paths[k_desc]
                    mesh_desc = k_desc
                    break
            if mesh_repo is None:
                raise Exception(f"Couldn't find local repo for: {m[0]}")
            if "/" in mesh_desc:
                mesh_src = mesh_repo.joinpath(mesh_desc.replace(mesh_desc.split("/")[-1], "")).joinpath(m[0])
            else:
                mesh_src = mesh_repo.joinpath(m[0])
            assert mesh_src.exists(), f"Not found: {mesh_src}"
            mesh_dst = dst_root.joinpath(m[0])
            if not mesh_dst.parent.exists():
                mesh_dst.parent.mkdir(parents=True)
            # Copy the mesh file to the Unity project.
            copy_file(src=str(mesh_src.resolve()), dst=str(mesh_dst.resolve()))
        if not self._quiet:
            print("Copied the .urdf and the meshes to the Unity project.")
        return urdf_dst

    def xacro_to_urdf(self, xacro_path: Path, repo_paths: Dict[str, Path], args: Dict[str, str] = None) -> Path:
        """
        Convert a local .xacro file to a .urdf file.

        :param xacro_path: The path to the local .xacro file.
        :param args: Names and values for the `arg` tags in the .xacro file.
        :param repo_paths: Local paths to all required repos. Key = The description infix. Value = The local repo path.

        :return: The path to the .urdf file.
        """

        if not RobotCreator.TEMP_ROOT.exists():
            RobotCreator.TEMP_ROOT.mkdir(parents=True)

        xacro = xacro_path.read_text(encoding="utf-8")

        # Set the args.
        if args is None:
            args = {"gazebo": 'false'}
        for k in args:
            xacro = re.sub('<xacro:arg name="' + k + '" default="(.*)"',
                           f'<xacro:arg name="{k}" default="{args[k]}"', xacro)
        xacro = re.sub(r'<xacro:include (.*)gazebo(.*?)/>', "", xacro)

        # Put all required .xacro files in a temporary directory.
        xacro_dir = RobotCreator.TEMP_ROOT.joinpath("xacro")
        if not xacro_dir.exists():
            xacro_dir.mkdir(parents=True)
        x = xacro_dir.joinpath(xacro_path.name)
        x.write_text(xacro, encoding="utf-8")

        xacros: List[Path] = [x]
        checked: List[Path] = []
        while len(xacros) > 0:
            xp = xacros.pop(0)
            checked.append(xp)
            xacro = xp.read_text(encoding="utf-8")
            for description in re.findall(r"\$\(find (.*?)\)", xacro, flags=re.MULTILINE):
                xacro_repo: Optional[Path] = None
                desc = ""
                for k_desc in repo_paths:
                    if description in k_desc:
                        xacro_repo = repo_paths[k_desc]
                        desc = k_desc
                        break
                assert xacro_repo is not None, f"Couldn't find: {description} in {xacro_repo} for {xp}"
                src_urdf_dir = xacro_repo.joinpath(desc).joinpath("urdf")
                for root_dir, dirs, files in walk(str(src_urdf_dir.resolve())):
                    for f in files:
                        src = Path(root_dir).joinpath(f)
                        if src.is_file() and src.suffix == ".xacro":
                            dst = xacro_dir.joinpath(src.name)
                            if not dst.exists():
                                copy_file(src=str(src.resolve()), dst=str(dst.resolve()))
                            if src not in xacros and src not in checked:
                                xacros.append(src)
        if not self._quiet:
            print("Copied all required xacro files to a temp directory.")
        # "Repair" all of the required .xacro files.
        for f in xacro_dir.iterdir():
            if f.is_file() and f.suffix == ".xacro":
                xacro = f.read_text(encoding="utf-8")
                xacro = re.sub(r"include filename=\"\$\((.*)\)/(.*)/(.*)\"", r'include filename="\3"', xacro)
                f.write_text(xacro, encoding="utf-8")
        # Finally, create the .urdf file.
        cwd = getcwd()
        chdir(str(RobotCreator.TEMP_ROOT.joinpath("xacro").resolve()))
        urdf_name = x.name.replace(".urdf.xacro", ".urdf").replace(".xacro", ".urdf")
        xacro_call = ["source", "/opt/ros/melodic/setup.bash", "&&",
                      "rosrun", "xacro", "xacro", "-o", urdf_name, x.name]
        if system() == "Windows":
            xacro_call.insert(0, "wsl")
        call(xacro_call)
        urdf_path = Path(f"../../Assets/robots/{urdf_name}")
        if urdf_path.exists():
            urdf_path.unlink()
        move_file(src=str(x.parent.joinpath(urdf_name).resolve()), dst=str(urdf_path.resolve()))
        if not self._quiet:
            print(f"Created {str(urdf_path.resolve())}")
        urdf_path = Path(str(urdf_path.resolve()))
        chdir(cwd)
        # Delete temp xacro files.
        remove_tree(str(xacro_dir.resolve()))
        assert urdf_path.exists(), f"Not found: {urdf_path.resolve()}"
        return urdf_path.resolve()

    def urdf_to_prefab(self, urdf_path: Path, immovable: bool = True, up: str = "y") -> Path:
        """
        Convert a .urdf file to Unity prefab.

        The .urdf file must already exist on this machine and its meshes must be at the expected locations.

        :param urdf_path: The path to the .urdf file.
        :param immovable: If True, the base of the robot will be immovable by default (see the `set_immovable` command).
        :param up: The up direction. Used for importing the .urdf into Unity. Options: "y" or "z".

        :return: The path to the .prefab file.
        """

        # Get the expected name of the robot.
        urdf = urdf_path.read_text(encoding="utf-8")
        name = re.search(r'<robot name="(.*?)"', urdf, flags=re.MULTILINE).group(1).strip()

        urdf_call = self.get_base_unity_call()[:]
        urdf_call.extend(["-executeMethod", "Creator.CreatePrefab",
                          f"-urdf='{str(urdf_path.resolve())}'",
                          f"-immovable={'true' if immovable else 'false'}",
                          f"-up={up}"])
        if not self._quiet:
            print("Creating a .prefab from a .urdf file...")
        call(urdf_call)
        RobotCreator._check_log()
        prefab_path = self._project_path.joinpath(f"Assets/prefabs/{name}.prefab")
        assert prefab_path.exists(), f"Prefab not found: {prefab_path}"
        if not self._quiet:
            print("...Done!")
        return prefab_path

    def prefab_to_asset_bundles(self, name: str) -> Dict[str, Path]:
        """
        Create asset bundles from a prefab.

        :param name: The name of the robot (minus the .prefab extension).

        :return: A dictionary. Key = The system platform. Value = The path to the asset bundle as a Path object.
        """

        asset_bundles_call = self.get_base_unity_call()[:]
        asset_bundles_call.extend(["-executeMethod", "Creator.CreateAssetBundles",
                                   f"-robot='{name}'"])
        if not self._quiet:
            print("Creating asset bundles...")
        call(asset_bundles_call)
        RobotCreator._check_log()
        # Verify that the asset bundles exist.
        asset_bundles_root_dir = self._project_path.joinpath(f"Assets/asset_bundles/{name}")
        asset_bundle_paths: Dict[str, Path] = dict()
        for build_target in UNITY_TO_SYSTEM:
            asset_bundle_path = asset_bundles_root_dir.joinpath(f"{build_target}/{name}")
            asset_bundle_path = Path(str(Path(asset_bundle_path.resolve())))
            assert asset_bundle_path.exists(), f"Couldn't find asset bundle: {asset_bundle_path.resolve()}"
            asset_bundle_paths[UNITY_TO_SYSTEM[build_target]] = asset_bundle_path
        if not self._quiet:
            print("...Done!")
        return asset_bundle_paths

    def get_unity_project(self) -> Path:
        """
        Build the asset_bundle_creator Unity project.

        :return The path to the asset_bundle_creator Unity project.
        """

        unity_project_path = self.get_project_path()

        # If the project already exists, stop.
        if unity_project_path.exists():
            assert unity_project_path.joinpath("Assets").exists(), f"There is a directory at {unity_project_path} but it's not a Unity project."
            return unity_project_path

        # Clone the repo.
        cwd = getcwd()
        chdir(str(Path.home().resolve()))
        call(["git", "clone", "https://github.com/alters-mit/robot_creator"])
        chdir(cwd)
        assert unity_project_path.exists(), f"Can't find project path: {unity_project_path}"
        return unity_project_path

    @staticmethod
    def get_project_path() -> Path:
        """
        :return: The expected path of the Unity project.
        """

        return Path.home().joinpath("robot_creator")

    @staticmethod
    def _check_log() -> None:
        """
        Check the Editor log for errors.
        """

        log = EDITOR_LOG_PATH.read_text(encoding="utf-8")
        if "failure" in log.lower() or "exception" in log.lower():
            raise Exception(f"There are errors in the Editor log!")

    @staticmethod
    def _page_to_raw(url: str) -> str:
        """
        Convert the URL of a GitHub page to the URL of the corresponding text file.

        :param url: A URL to a GitHub page.

        :return: The URL to the corresponding text file.
        """

        if "https://github.com" in url:
            return re.sub(r"https://github\.com/(.*)/blob/(.*)", r"https://raw.githubusercontent.com/\1/\2", url)
        elif "https://raw.githubusercontent.com" in url:
            return url
        else:
            raise Exception(f"Unexpected URL: {url}")

    @staticmethod
    def _raw_to_page(url: str):
        """
        Convert the URL of a raw text file to the corresponding GitHub page.

        :param url: A URL to a text file page.

        :return: The URL to the corresponding GitHub page.
        """

        if "https://github.com" in url:
            return url
        elif "https://raw.githubusercontent.com" in url:
            return re.sub(r"https://raw\.githubusercontent\.com/(.*)/master/(.*)",
                          r"https://github.com/\1/blob/master/\2", url)
        else:
            raise Exception(f"Unexpected URL: {url}")

    @staticmethod
    def _get_repo_url(url: str) -> str:
        """
        :param url: The URL of the .urdf or .xacro file.

        :return: The base repo of a .urdf or .xacro file.
        """

        page_url = RobotCreator._raw_to_page(url=url)
        return re.sub(r"https://github\.com/(.*)/blob/(.*)", r"https://github.com/\1", page_url)

    @staticmethod
    def _get_repo_name(repo_url: str) -> str:
        """
        :param repo_url: The base URL of a repo.

        :return: The expected name of the repo.
        """

        return repo_url.split("/")[-1]

    @staticmethod
    def _get_local_repo_path(url: str) -> Path:
        """
        :param url: The URL of the .urdf or .xacro file.

        :return: The path to the local repo.
        """

        if not RobotCreator.TEMP_ROOT.exists():
            RobotCreator.TEMP_ROOT.mkdir(parents=True)

        repo_url = RobotCreator._get_repo_url(url=url)
        repo_name = RobotCreator._get_repo_name(repo_url=repo_url)
        return RobotCreator.TEMP_ROOT.joinpath(repo_name)

    @staticmethod
    def _get_description_infix(url: str) -> str:
        """
        :param url: The URL of the .urdf or .xacro file.

        :return: The string between the repo URL and the /urdf/ directory.
        """

        page = RobotCreator._raw_to_page(url=url)
        s = re.search(r"(.*)/blob/master/(.*)/urdf", page)
        if s is None:
            return re.search(r"(.*)/blob/master/((.*)_description)/", page).group(2)
        else:
            return s.group(2)
