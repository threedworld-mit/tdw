from typing import List, Dict, Optional, Union
from os import getcwd, chdir, walk, devnull
import re
from platform import system
from pathlib import Path
from subprocess import call
from shutil import rmtree, copyfile, move
from tdw.tdw_utils import TDWUtils
from tdw.asset_bundle_creator.asset_bundle_creator import AssetBundleCreator


class RobotCreator(AssetBundleCreator):
    """
    Download a .urdf or .xacro file and convert it into an asset bundle that is usable by TDW.
    """

    """:class_var
    The root temporary directory.
    """
    TEMP_ROOT: Path = AssetBundleCreator.PROJECT_PATH.joinpath("temp_robots")

    def source_url_to_asset_bundles(self, url: str, output_directory: Union[str, Path],
                                    required_repo_urls: Dict[str, str] = None,
                                    xacro_args: Dict[str, str] = None, immovable: bool = True,
                                    description_infix: str = None, branch: str = None,
                                    library_path: Union[str, Path] = None, library_description: str = None,
                                    source_description: str = None) -> None:
        """
        Given the URL of a .urdf file or a .xacro file, create asset bundles of the robot.

        This is a wrapper function for:

        1. `self.clone_repo()`
        2. `self.xacro_to_urdf()` (if applicable)
        3. `self.urdf_to_prefab()`
        4. `self.prefab_to_asset_bundles()`
        5. `self.create_record()`

        Example `urdf_url`:

        ```
        https://github.com/ros-industrial/robot_movement_interface/blob/master/dependencies/ur_description/urdf/ur5_robot.urdf
        ```

        Example `output_directory`:

        ```
        output_directory/
        ....Darwin/
        ........robot
        ....Linux/
        ........robot
        ....Windows/
        ........robot
        ....log.txt
        ....record.json
        ....model.json
        ....library.json
        ```

        - `Darwin/robot`, `Linux/robot` and `Windows/robot` are the platform-specific asset bundles.
        - `log.txt` is a log from the `asset_bundle_creator` Unity Editor project.
        - `record.json` is a serialized `RobotRecord`.
        - `model.json` is a JSON dump of the converted .urdf file and mesh paths.
        - `library.json` is a serialized `RobotLibrarian`. It will only be added/set if the optional `library_path` is set.

        :param url: The URL of a .urdf or a .xacro file.
        :param output_directory: The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this directory doesn't exist, it will be created.
        :param required_repo_urls: A dictionary of description folder names and repo URLs outside of the robot's repo that are required to create the robot. This is only required for .xacro files that reference outside repos. For example, the Sawyer robot requires this to add the gripper: `{"intera_tools_description": "https://github.com/RethinkRobotics/intera_common"}`
        :param xacro_args: Names and values for the `arg` tags in the .xacro file (ignored if this is a .urdf file). For example, the Sawyer robot requires this to add the gripper: `{"electric_gripper": "true"}`
        :param immovable: If True, the base of the robot is immovable.
        :param description_infix: The name of the description infix within the .urdf URL, such as `fetch_description`. Only set this if the urdf URL is non-standard; otherwise `RobotCreator` should be able to find this automatically.
        :param branch: The name of the branch of the repo. If None, defaults to `"master"`.
        :param library_path: If not None, this is a path as a string or [`Path`](https://docs.python.org/3/library/pathlib.html) to a new or existing `RobotLibrarian` .json file. The record will be added to this file in addition to being saved to `record.json`.
        :param library_description: A description of the library. Ignored if `library_path` is None.
        :param source_description: A description of the source of the .urdf file, for example the repo URL.
        """

        if required_repo_urls is None:
            required_repo_urls = list()
        if branch is None:
            branch = "master"
        # Clone the repo.
        repo_paths: Dict[str, Path] = dict()
        local_repo_path = self.clone_repo(url=url, branch=branch)
        if description_infix is None:
            description_infix = RobotCreator._get_description_infix(url=url, branch=branch)
        repo_paths[description_infix] = local_repo_path
        # Clone the required repos.
        for description in required_repo_urls:
            required_repo_url = required_repo_urls[description]
            required_local_repo_path = self.clone_repo(url=required_repo_url)
            repo_paths[description] = required_local_repo_path
        urdf_path = self.get_urdf_path_from_local_repo(local_repo_path=local_repo_path,
                                                       url=url, branch=branch)
        # Convert the .xacro file to a .urdf file.
        if Path(url).suffix == ".xacro":
            urdf_path = self.xacro_to_urdf(xacro_path=urdf_path, repo_paths=repo_paths, args=xacro_args)
            assert urdf_path.exists(), f"Not found: {urdf_path.resolve()}"
        self.source_file_to_asset_bundles(source_file=urdf_path, output_directory=output_directory,
                                          immovable=immovable, library_path=library_path,
                                          library_description=library_description,
                                          source_description=source_description)

    def source_file_to_asset_bundles(self, source_file: Union[str, Path], output_directory: Union[str, Path],
                                     immovable: bool = True, library_path: Union[str, Path] = None,
                                     library_description: str = None, source_description: str = None) -> None:
        """
        Given a .urdf file plus its meshes, create asset bundles of the robot.

        This is a wrapper function for:

        1. `self.urdf_to_prefab()`
        2. `self.prefab_to_asset_bundles()`
        3. `self.create_record()`

        Example source directory:

        ```
        ur_description/
        ....urdf/
        ........ur5_robot.urdf
        ....meshes/
        ........ur5/
        ............visual/
        ................Base.dae
        ................Forearm.dae
        ................Shoulder.dae
        ................UpperArm.dae
        ................Wrist1.dae
        ................Wrist2.dae
        ................Wrist3.dae
        ```

        - The directory structure must match that of the [source repo](https://github.com/ros-industrial/robot_movement_interface).
        - Collision meshes are ignored; they will be generated when creating the prefab.

        Example `output_directory`:

        ```
        output_directory/
        ....Darwin/
        ........robot
        ....Linux/
        ........robot
        ....Windows/
        ........robot
        ....log.txt
        ....record.json
        ....model.json
        ....library.json
        ```

        - `Darwin/robot`, `Linux/robot` and `Windows/robot` are the platform-specific asset bundles.
        - `log.txt` is a log from the `asset_bundle_creator` Unity Editor project.
        - `record.json` is a serialized `RobotRecord`.
        - `model.json` is a JSON dump of the converted .urdf file and mesh paths.
        - `library.json` is a serialized `RobotLibrarian`. It will only be added/set if the optional `library_path` is set.

        :param source_file: The path to the source .fbx or .obj file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html).
        :param output_directory: The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this directory doesn't exist, it will be created.
        :param immovable: If True, the base of the robot is immovable.
        :param library_path: If not None, this is a path as a string or [`Path`](https://docs.python.org/3/library/pathlib.html) to a new or existing `RobotLibrarian` .json file. The record will be added to this file in addition to being saved to `record.json`.
        :param library_description: A description of the library. Ignored if `library_path` is None.
        :param source_description: A description of the source of the .urdf file, for example the repo URL.
        """

        args = self._get_source_destination_args(name=RobotCreator.get_name(source_file),
                                                 source=source_file,
                                                 destination=output_directory)
        if immovable:
            args.append("-immovable")
        if source_description is not None:
            args.append(f'-source_description="{source_description}"')
        args = AssetBundleCreator._add_library_args(args=args,
                                                    library_path=library_path,
                                                    library_description=library_description)
        self.call_unity(method="SourceFileToAssetBundles",
                        args=args,
                        log_path=AssetBundleCreator._get_log_path(output_directory))

    def clone_repo(self, url: str, branch: str = None) -> Path:
        """
        Clone a repo to a temporary directory.

        :param url: The URL to the .urdf or .xacro file or the repo.
        :param branch: The name of the branch of the repo. If None, defaults to `"master"`.

        :return: The temporary directory.
        """

        if not RobotCreator.TEMP_ROOT.exists():
            RobotCreator.TEMP_ROOT.mkdir(parents=True)
        if branch is None:
            branch = "master"
        # This is a .urdf or .xacro file. Parse the repo URL accordingly.
        if url.endswith(".xacro") or url.endswith(".urdf"):
            local_repo_path = RobotCreator._get_local_repo_path(url=url, branch=branch)
            repo_url = RobotCreator._get_repo_url(url=url, branch=branch)
        # This is the base URL of the repo. Parse it accordingly.
        else:
            local_repo_path = RobotCreator.TEMP_ROOT.joinpath(Path(url).name)
            repo_url = url
        if local_repo_path.exists():
            return local_repo_path
        # Change directory.
        cwd = getcwd()
        chdir(str(RobotCreator.TEMP_ROOT.resolve()))
        if not self.quiet:
            print(f"Cloning: {repo_url}")
        # Clone the repo.
        call(["git", "clone", repo_url],
             stderr=open(devnull, "wb"))
        chdir(cwd)
        assert local_repo_path.exists(), f"Can't find: {local_repo_path.resolve()}"
        if not self.quiet:
            print("...Done!")
        return local_repo_path

    def get_urdf_path_from_local_repo(self, url: str, local_repo_path: Path, branch: str = None) -> Path:
        """
        :param url: The URL to a .urdf file.
        :param local_repo_path: The path to a local repo.
        :param branch: The branch. If None, defaults to `"master"`.

        :return: The path to the local .urdf file.
        """

        if branch is None:
            branch = "master"
        # Get the page URL.
        page_url = self._raw_to_page(url=url, branch=branch)
        # Get the repo path.
        repo_path = re.search(r"(.*)/blob/" + branch + r"/(.*)", page_url).group(2)
        return local_repo_path.joinpath(repo_path)

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
                                copyfile(src=str(src.resolve()), dst=str(dst.resolve()))
                            if src not in xacros and src not in checked:
                                xacros.append(src)
        if not self.quiet:
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
        urdf_path = xacro_path.parent.joinpath(urdf_name)
        if urdf_path.exists():
            urdf_path.unlink()
        move(src=str(x.parent.joinpath(urdf_name).resolve()), dst=str(urdf_path.resolve()))
        if not self.quiet:
            print(f"Created {str(urdf_path.resolve())}")
        urdf_path = Path(str(urdf_path.resolve()))
        chdir(cwd)
        # Delete temp xacro files.
        rmtree(str(xacro_dir.resolve()))
        assert urdf_path.exists(), f"Not found: {urdf_path.resolve()}"
        return urdf_path.resolve()

    def urdf_to_prefab(self, urdf_path: Union[str, Path], output_directory: Union[str, Path], immovable: bool = True) -> None:
        """
        Convert a .urdf file to Unity prefab.

        The .urdf file must already exist on this machine and its meshes must be at the expected locations.

        :param urdf_path: The path to the .urdf file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html).
        :param output_directory: The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this directory doesn't exist, it will be created.
        :param immovable: If True, the base of the robot will be immovable by default (see the `set_immovable` command).
        """

        args = self._get_source_destination_args(name=RobotCreator.get_name(urdf_path),
                                                 source=urdf_path,
                                                 destination=output_directory)
        if immovable:
            args.append("-immovable")
        self.call_unity(method="SourceFileToPrefab",
                        args=args,
                        log_path=AssetBundleCreator._get_log_path(output_directory))

    def create_record(self, name: str, output_directory: Union[str, Path],
                      library_path: Union[str, Path] = None, library_description: str = None,
                      source_description: str = None, immovable: bool = True) -> None:
        """
        Create a model record and save it to disk. This requires asset bundles of the robot to already exist:

        ```
        output_directory/
        ....Darwin/
        ........robot
        ....Linux/
        ........robot
        ....Windows/
        ........robot
        ....log.txt
        ```

        Result:

        ```
        output_directory/
        ....Darwin/
        ........robot
        ....Linux/
        ........robot
        ....Windows/
        ........robot
        ....record.json
        ....log.txt
        library.json
        ```

        - `record.json` is a serialized `RobotRecord`.
        - `library.json` is a serialized `RobotLibrarian`. It will only be added/set if the optional `library_path` is set.

        :param name: The name of the robot.
        :param output_directory: The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this directory doesn't exist, it will be created.
        :param library_path: If not None, this is a path as a string or [`Path`](https://docs.python.org/3/library/pathlib.html) to a new or existing `RobotLibrarian` .json file. The record will be added to this file in addition to being saved to `record.json`.
        :param library_description: A description of the library. Ignored if `library_path` is None.
        :param source_description: A description of the source of the .urdf file, for example the repo URL.
        :param immovable: If True, the base of the robot is immovable.
        """

        args = self._get_source_destination_args(name=name,
                                                 source="dummy",
                                                 destination=output_directory)
        if source_description is not None:
            args.append(f'-source_description="{source_description}"')
        if immovable:
            args.append('-immovable')
        args = AssetBundleCreator._add_library_args(args=args,
                                                    library_path=library_path,
                                                    library_description=library_description)
        self.call_unity(method="CreateRecord",
                        args=args,
                        log_path=AssetBundleCreator._get_log_path(output_directory))

    @staticmethod
    def get_name(urdf_path: Union[str, Path]) -> str:
        """
        :param urdf_path: The path to the .urdf file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html).

        :return: The expected name of the robot.
        """

        return re.search(r'<robot(.*?)name=[\'|"](.*?)[\'|"]',
                         TDWUtils.get_path(urdf_path).read_text(encoding="utf-8"),
                         flags=re.MULTILINE).group(2).strip()

    def get_creator_class_name(self) -> str:
        return "RobotCreator"

    @staticmethod
    def fix_urdf(urdf_path: Union[str, Path], remove_gazebo: bool = True, simplify_namespaces: bool = True,
                 link_name_excludes_regex: List[str] = None, link_exclude_types: List[str] = None) -> Path:
        """
        "Fix" a .urdf file by removing extraneous information. This function will:

        - Make the file easier to parse, for example by removing gazebo elements and simplifying XML namespaces.
        - Remove unneeded links, for example laser or camera links.

        This function won't alter the original .urdf file and will create a new .urdf file.

        :param urdf_path: The path to the .urdf file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html).
        :param remove_gazebo: If True, remove all `<gazebo>` elements. This should usually be True.
        :param simplify_namespaces: If True, simplify the XML namespaces. This should usually be True.
        :param link_name_excludes_regex: A list of regular expressions to search for in links, for example `["_gazebo_"]`. Link names that match this will be removed.
        :param link_exclude_types: Some links have a `type` attribute. Exclude links matching this types in this list, for example `["laser", "camera"]`.

        :return: The path to the "fixed" .urdf file.
        """

        path = TDWUtils.get_path(urdf_path)
        text = path.read_text(encoding="utf-8")
        # Remove gazebo elements.
        if remove_gazebo:
            text = re.sub(r'(<gazebo((.|\n)*?)</gazebo>)', '', text, flags=re.MULTILINE)
        # Simplify namespaces.
        if simplify_namespaces:
            text = re.sub(r'<robot(.*?)name="(.*?)"(.*)>', r'<robot xmlns:xacro="http://ros.org/wiki/xacro" name="\2">',
                          text, flags=re.MULTILINE)
        # Exclude these links and joints.
        if link_name_excludes_regex is not None:
            for link_name_exclude_regex in link_name_excludes_regex:
                text = re.sub(r'<link name="(.*?)' + link_name_exclude_regex + r'(.*?)"(/>|((.|\n)*?)</link>)',
                              '', text, flags=re.MULTILINE)
        if link_exclude_types is not None:
            for link_exclude_type in link_exclude_types:
                text = re.sub(r'<link(.*?)type="' + link_exclude_type + r'"(/>|((.|\n)*?)</link>)',
                              '', text, flags=re.MULTILINE)
        dst: Path = path.parent.joinpath(f'{path.name[:-5]}_fixed.urdf')
        dst.write_text(text)
        return dst

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
    def _raw_to_page(url: str, branch: str) -> str:
        """
        Convert the URL of a raw text file to the corresponding GitHub page.

        :param url: A URL to a text file page.
        :param branch: The branch name.

        :return: The URL to the corresponding GitHub page.
        """

        if "https://github.com" in url:
            return url
        elif "https://raw.githubusercontent.com" in url:
            return re.sub(r"https://raw\.githubusercontent\.com/(.*)/" + branch + r"/(.*)",
                          r"https://github.com/\1/blob/" + branch + r"/\2", url)
        else:
            raise Exception(f"Unexpected URL: {url}")

    @staticmethod
    def _get_repo_url(url: str, branch: str) -> str:
        """
        :param url: The URL of the .urdf or .xacro file.
        :param branch: The branch name.

        :return: The base repo of a .urdf or .xacro file.
        """

        page_url = RobotCreator._raw_to_page(url=url, branch=branch)
        return re.sub(r"https://github\.com/(.*)/blob/(.*)", r"https://github.com/\1", page_url)

    @staticmethod
    def _get_repo_name(repo_url: str) -> str:
        """
        :param repo_url: The base URL of a repo.

        :return: The expected name of the repo.
        """

        return repo_url.split("/")[-1]

    @staticmethod
    def _get_local_repo_path(url: str, branch: str) -> Path:
        """
        :param url: The URL of the .urdf or .xacro file.
        :param branch: The branch name.

        :return: The path to the local repo.
        """

        if not RobotCreator.TEMP_ROOT.exists():
            RobotCreator.TEMP_ROOT.mkdir(parents=True)
        repo_url = RobotCreator._get_repo_url(url=url, branch=branch)
        repo_name = RobotCreator._get_repo_name(repo_url=repo_url)
        return RobotCreator.TEMP_ROOT.joinpath(repo_name)

    @staticmethod
    def _get_description_infix(url: str, branch: str) -> str:
        """
        :param url: The URL of the .urdf or .xacro file.
        :param branch: The branch name.

        :return: The string between the repo URL and the /urdf/ directory.
        """

        page = RobotCreator._raw_to_page(url=url, branch=branch)
        s = re.search(r"(.*)/blob/" + branch + r"/(.*)/urdf", page)
        if s is None:
            return re.search(r"(.*)/blob/" + branch + r"/((.*)_description)/", page).group(2)
        else:
            return s.group(2)
