from typing import List, Dict
from os.path import join
from os import getcwd, chdir, walk, devnull
from csv import DictReader
import re
from platform import system
from pathlib import Path
from subprocess import call
from distutils.file_util import copy_file, move_file
from distutils.dir_util import remove_tree
import pkg_resources
from requests import get, head
from tdw.asset_bundle_creator_base import AssetBundleCreatorBase
from tdw.backend.paths import EDITOR_LOG_PATH
from tdw.backend.platforms import UNITY_TO_SYSTEM


class RobotRepo:
    def __init__(self, url: str, description: str):
        """
        :param url: The URL of the repo.
        :param description: The name of the folder with the urdfs and meshes.
        """

        self.url: str = url
        self.description: str = description


class RobotCreator(AssetBundleCreatorBase):
    # Descriptions per repo. Key = The description string. Value = The repo name.
    DESCRIPTIONS: Dict[str, str] = dict()
    # All known remote repos.
    REMOTE_REPOS: Dict[str, RobotRepo] = dict()
    # Load all known repo URLs.
    with open(pkg_resources.resource_filename(__name__, "robotics/repos.csv")) as f:
        __reader = DictReader(f)
        for __row in __reader:
            REMOTE_REPOS[__row["url"].split("/")[-1]] = RobotRepo(url=__row["url"], description=__row["description"])
            DESCRIPTIONS[__row["description"]] = __row["url"].split("/")[-1]
    # The root temporary directory.
    TEMP_ROOT = Path.home().joinpath("robot_creator/temp_robots")
    if not TEMP_ROOT.exists():
        TEMP_ROOT.mkdir(parents=True)

    def import_unity_package(self, unity_project_path: Path) -> None:
        """
        Import the .unitypackage file into the Unity project. Add the .urdf importer package.

        :param unity_project_path: The path to the Unity project.
        """

        urdf_call = self.get_base_unity_call()[:]
        urdf_call.extend(["-executeMethod", "RosImporter.Import"])
        call(urdf_call)
        super().import_unity_package(unity_project_path=unity_project_path)

    @staticmethod
    def download_repo(url: str) -> Path:
        """
        Download the repo to a temporary directory.

        :param url: The repo URL.

        :return: The temporary directory.
        """

        # Get or create the temporary directory.

        # Change directory.
        cwd = getcwd()
        chdir(str(RobotCreator.TEMP_ROOT.resolve()))
        # Clone the repo.
        call(["git", "clone", url])
        chdir(cwd)
        repo_path = RobotCreator.TEMP_ROOT.joinpath(url.split("/")[-1])
        assert repo_path.exists(), f"Can't find: {repo_path.resolve()}"
        return repo_path

    def xacro_to_urdf(self, url: str, args: Dict[str, str] = None) -> Path:
        """
        Download a .xacro file and all of its dependencies and convert it to a .urdf file.

        :param url: The URL to the .xacro file. This must be the "raw" file, not a GitHub html page.
        :param args: Names and values for the `arg` tags in the .xacro file.

        :return: The path to the .urdf file.
        """

        resp = get(url)
        assert resp.status_code == 200, f"Tried to download {url} but got error code {resp.status_code}"
        xacro = resp.content.decode("utf-8")
        if not self.quiet:
            print(f"Got {url}")

        if args is None:
            args = {"gazebo": '"false"'}

        # Set the args.
        if args is not None:
            for k in args:
                xacro = re.sub('<xacro:arg name="' + k + '" default="(.*)"',
                               f'<xacro:arg name="{k}" default="{args[k]}"', xacro)
        xacro_dir = RobotCreator.TEMP_ROOT.joinpath("xacro")
        if not xacro_dir.exists():
            xacro_dir.mkdir(parents=True)

        x = xacro_dir.joinpath(Path(url).name)
        x.write_text(xacro, encoding="utf-8")
        xacros: List[Path] = [x]
        checked: List[Path] = []
        while len(xacros) > 0:
            xp = xacros.pop(0)
            xacro = xp.read_text(encoding="utf-8")
            for find in re.findall(r"\$\(find (.*?)\)", xacro, flags=re.MULTILINE):
                repo_name = RobotCreator.DESCRIPTIONS[find]
                local_repo = RobotCreator.TEMP_ROOT.joinpath(repo_name)
                if not local_repo.exists():
                    if not self.quiet:
                        print(f"Couldn't find {local_repo}. Cloning...")
                    RobotCreator.download_repo(RobotCreator.REMOTE_REPOS[repo_name].url)
                    if not self.quiet:
                        print("...Done!")
                src_urdf_dir = local_repo.joinpath(RobotCreator.REMOTE_REPOS[repo_name].description + "/urdf")
                for root_dir, dirs, files in walk(str(src_urdf_dir.resolve())):
                    for f in files:
                        src = Path(root_dir).joinpath(f)
                        if src.is_file() and src.suffix == ".xacro":
                            dst = xacro_dir.joinpath(src.name)
                            if not dst.exists():
                                copy_file(src=str(src.resolve()), dst=str(dst.resolve()))
                            if src not in checked:
                                xacros.append(src)
                                checked.append(xp)
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
        urdf_name = x.name.replace(".xacro", "")
        xacro_call = ["source", "/opt/ros/melodic/setup.bash", "&&",
                      "rosrun", "xacro", "xacro", "-o", urdf_name, x.name]
        if system() == "Windows":
            xacro_call.insert(0, "wsl")
        call(xacro_call)
        urdf_path = Path(f"../../Assets/robots/{urdf_name}")
        if urdf_path.exists():
            urdf_path.unlink()
        move_file(src=str(Path(urdf_name).resolve()), dst=str(urdf_path.resolve()))
        if not self.quiet:
            print(f"Created {str(urdf_path.resolve())}")
        urdf_path = Path(str(urdf_path.resolve()))
        chdir(cwd)
        # Delete temp xacro files.
        remove_tree(str(xacro_dir.resolve()))
        return urdf_path.resolve()

    def download_urdf(self, url: str) -> Path:
        """
        Download a .urdf file to the robot_creator project.

        :param url:  The URL to the .urdf file. This must be the "raw" file, not a GitHub html page.

        :return: The local path of the downloaded file.
        """

        resp = get(url)
        assert resp.status_code == 200, f"Tried to download {url} but got error code {resp.status_code}"
        p = self.project_path.joinpath(f"Assets/robots/{url.split('/')[-1]}")
        p.write_text(resp.content.decode("utf-8"), encoding="utf-8")
        return p

    def urdf_to_prefab(self, urdf_path: Path, immovable: bool = True, up: str = "y") -> Path:
        """
        Convert a .urdf file to Unity prefab.

        The .urdf file must already exist on this machine and its meshes must be at the expected locations.

        See: `download_urdf()`, `download_and_convert_xacro()`, and `download_meshes()`.

        :param urdf_path: The path to the .urdf file.
        :param immovable: If True, the base of the robot will be immovable by default (see the `set_immovable` command).
        :param up: The up direction. Used for importing the .urdf into Unity. Options: "y" or "z".

        :return: The path to the .prefab file.
        """

        urdf_call = self.get_base_unity_call()[:]
        urdf_call.extend(["-executeMethod", "Creator.CreatePrefab",
                          f"-urdf='{str(urdf_path.resolve())}'",
                          f"-immovable={'true' if immovable else 'false'}",
                          f"-up={up}"])
        if not self.quiet:
            print("Creating a .prefab from a .urdf file...")
        call(urdf_call)
        RobotCreator.check_log()
        prefab_path = self.project_path.joinpath(f"Assets/prefabs/{urdf_path.name.replace('urdf', 'prefab')}")
        assert prefab_path.exists(), f"Prefab not found: {prefab_path}"
        if not self.quiet:
            print("...Done!")
        return prefab_path

    def prefab_to_asset_bundle(self, name: str) -> List[Path]:
        asset_bundles_call = self.get_base_unity_call()[:]
        asset_bundles_call.extend(["-executeMethod", "Creator.CreateAssetBundles",
                                   f"-robot='{name}'"])
        if not self.quiet:
            print("Creating asset bundles...")
        call(asset_bundles_call)
        RobotCreator.check_log()
        # Verify that the asset bundles exist.
        asset_bundles_root_dir = self.project_path.joinpath(f"Assets/asset_bundles/{name}")
        asset_bundle_paths: List[Path] = list()
        for build_target in UNITY_TO_SYSTEM:
            asset_bundle_path = asset_bundles_root_dir.joinpath(f"{build_target}/{name}")
            asset_bundle_path = Path(str(Path(asset_bundle_path.resolve())))
            assert asset_bundle_path.exists(), f"Couldn't find asset bundle: {asset_bundle_path.resolve()}"
            asset_bundle_paths.append(asset_bundle_path)
        if not self.quiet:
            print("...Done!")
        return asset_bundle_paths

    def download_meshes(self, urdf_path: Path) -> None:
        """
        Download all mesh files referenced by the .urdf file.
        From this mesh file, create a hull colliders .obj file.

        :param urdf_path: The path to the .urdf file.
        """

        urdf = urdf_path.read_text(encoding="utf-8")
        dst = self.project_path.joinpath("Assets/robots")
        if not dst.exists():
            dst.mkdir(parents=True)

        # We'll use these binaries to create colliders.
        assimp = pkg_resources.resource_filename(__name__, self.binaries["assimp"])
        vhacd = pkg_resources.resource_filename(__name__, self.binaries["vhacd"])
        meshconv = pkg_resources.resource_filename(__name__, self.binaries["meshconv"])

        for m in re.findall(r"filename=\"package://((.*)\.(DAE|dae|stl|STL))\"", urdf):
            description = m[0].split("/")[0]
            repo_name = RobotCreator.DESCRIPTIONS[description]
            mesh_src = f"https://raw.githubusercontent.com/" \
                       f"{RobotCreator.REMOTE_REPOS[repo_name].url.replace('https://github.com/', '')}/master"
            mesh_src = join(mesh_src, m[0]).replace("\\", "/")
            resp = head(mesh_src)
            if resp.status_code != 200:
                raise Exception(f"Got error code {resp.status_code} for {mesh_src}")
            # Create the local directory for the mesh.
            mesh_dst = dst.joinpath(m[0])
            if not mesh_dst.parent.exists():
                mesh_dst.parent.mkdir(parents=True)
            # Save the mesh.
            mesh_dst.write_bytes(get(mesh_src).content)
            if not self.quiet:
                print(f"Downloaded: {mesh_dst}")
                print("Creating the colliders .obj file...")

            # Convert the dae to obj.
            mesh_obj = str(mesh_dst.resolve())[:-4] + ".obj"
            call([assimp,
                  "export",
                  str(mesh_dst.resolve()),
                  mesh_obj],
                 stdout=open(devnull, "wb"))
            # Remove the useless .mtl file.
            mtl_path = Path(str(mesh_dst.resolve())[:-4] + ".mtl")
            if mtl_path.exists():
                mtl_path.unlink()
            # Create the .wrl file.
            wrl_path = str(mesh_dst.resolve())[:-4] + ".wrl"
            call([vhacd,
                  "--input", mesh_obj,
                  "--resolution", str(100000),
                  "--output", wrl_path],
                 stdout=open(devnull, "wb"))
            # Remove an unwanted log file.
            log_file = Path("log.txt")
            if log_file.exists():
                log_file.unlink()
            # Convert the .wrl back to .obj
            call([meshconv,
                  wrl_path,
                  "-c",
                  "obj",
                  "-o",
                  mesh_obj[:-4],
                  "-sg"],
                 stdout=open(devnull, "wb"))
            # Remove the .wrl file.
            Path(wrl_path).unlink()
            if not self.quiet:
                print("...Done!")

    @staticmethod
    def get_record(name: str, source: str, immovable: bool):
        raise Exception("TODO")

    @staticmethod
    def get_unity_package() -> str:
        return "robot_creator.unitypackage"

    @staticmethod
    def get_project_path() -> Path:
        return Path.home().joinpath("robot_creator")

    @staticmethod
    def check_log() -> None:
        """
        Check the Editor log for errors.
        """

        log = EDITOR_LOG_PATH.read_text(encoding="utf-8")
        if "error" in log.lower() or "failure" in log.lower():
            raise Exception(f"There are errors in the Editor log!\n\n{log}")


if __name__ == "__main__":
    r = RobotCreator()

    up = r.xacro_to_urdf("https://raw.githubusercontent.com/RethinkRobotics/sawyer_robot/master/"
                         "sawyer_description/urdf/sawyer.urdf.xacro",
                         args={"electric_gripper": "true"})
    r.download_meshes(urdf_path=up)
    prefab = r.urdf_to_prefab(urdf_path=up)
    asset_bundles = r.prefab_to_asset_bundle("sawyer")
    print(asset_bundles)
