from os.path import join
from os import devnull
import re
from pathlib import Path
from subprocess import call
import pkg_resources
from requests import get, head
from tdw.asset_bundle_creator_base import AssetBundleCreatorBase


class RobotCreator(AssetBundleCreatorBase):
    def download_urdf(self, name: str, urdf_url: str, meshes_url: str) -> Path:
        """
        Download a .urdf file and all of its files. Convert all .stl files to .dae files.

        Create hull colliders from the .dae meshes using assimp, vhacd, and meshconv (this can take a while).

        :param name: The name of the robot.
        :param urdf_url: The URL to the .urdf file
        :param meshes_url: The URL prefix to the mesh files.

        :return: The path of the local directory that contains the .urdf file and the meshes.
        """

        # Get the .urdf text.
        urdf_text: str = get(urdf_url).content.decode("utf-8")
        # Ignore gazebo stuff.
        urdf_text = re.sub(r"<gazebo((.|\n)*)</gazebo>", "", urdf_text, re.MULTILINE)
        if not self.quiet:
            print(f"Got the .urdf file.")
        # Get the root destination directory.
        dst = self.get_project_path().joinpath(f"Assets/robots/{name}")
        if not dst.exists():
            dst.mkdir(parents=True)

        assimp = pkg_resources.resource_filename(__name__, self.binaries["assimp"])
        vhacd = pkg_resources.resource_filename(__name__, self.binaries["vhacd"])
        meshconv = pkg_resources.resource_filename(__name__, self.binaries["meshconv"])

        # Download all of the meshes.
        # Find these meshes by parsing the .urdf file.
        for m in re.findall(r"filename=\"package://((.*)\.(DAE|dae|stl|STL))\"", urdf_text):
            mesh_src = join(meshes_url, m[0])
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
                print(f"Downloaded {mesh_src} to:\n{mesh_dst}")

            # Unity can't handle .stl files so we need to convert them to .dae files.
            if mesh_dst.suffix.lower() == ".stl":
                mesh_dae = str(mesh_dst.resolve())[:-4] + ".dae"
                call([assimp,
                      "export",
                      str(mesh_dst.resolve()),
                      mesh_dae],
                     stdout=open(devnull, "wb"))
                # Delete the .stl file.
                mesh_dst.unlink()
                mesh_dst = Path(mesh_dae)
                if not self.quiet:
                    print("Converted the .stl file to a .dae file and removed the .stl file.")

            # Convert the dae to obj.
            mesh_obj = str(mesh_dst.resolve())[:-4] + ".obj"
            call([assimp,
                  "export",
                  str(mesh_dst.resolve()),
                  mesh_obj],
                 stdout=open(devnull, "wb"))
            if not self.quiet:
                print(f"Created a .obj file from the .dae file.")
            # Remove the useless .mtl file.
            mtl_path = Path(str(mesh_dst.resolve())[:-4] + ".mtl")
            if mtl_path.exists():
                mtl_path.unlink()
                if not self.quiet:
                    print("Removed the .mtl file.")

            # Create the .wrl file.
            wrl_path = str(mesh_dst.resolve())[:-4] + ".wrl"
            call([vhacd,
                  "--input", mesh_obj,
                  "--resolution", str(100000),
                  "--output", wrl_path],
                 stdout=open(devnull, "wb"))
            if not self.quiet:
                print("Created a .wrl file from the .obj file.")
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
            if not self.quiet:
                print("Created a .obj file from the .wrl file.")
            # Remove the .wrl file.
            Path(wrl_path).unlink()
        # Replace all references to .stl files with .dae
        urdf_text = re.sub(r"(stl|STL)", "dae", urdf_text)
        # Do some other minor fixes.
        urdf_text = urdf_text.replace('xml version="1"', 'xml version="1.0"')
        urdf_text = urdf_text.replace("<mass value=\"\\.0\"", "<mass value=\"5.0\"")
        # Save the .urdf file.
        urdf_path = dst.joinpath(name + ".urdf")
        urdf_path.write_text(urdf_text, encoding="utf-8")
        if not self.quiet:
            print(f"Saved the .urdf file: {urdf_path.resolve()}")
        return dst

    @staticmethod
    def get_unity_package() -> str:
        return "robot_creator.unitypackage"

    @staticmethod
    def get_project_path() -> Path:
        return Path.home().joinpath("robot_creator")


if __name__ == "__main__":
    r = RobotCreator()
    """
    r.download_urdf(name="sawyer",
                    urdf_url="https://raw.githubusercontent.com/bulletphysics/pybullet_robots/master/data/"
                             "sawyer_robot/sawyer_description/urdf/sawyer.urdf",
                    meshes_url="https://github.com/bulletphysics/pybullet_robots/raw/master/data/sawyer_robot/")
    """
    r.download_urdf(name="baxter",
                    urdf_url="https://raw.githubusercontent.com/RethinkRobotics/baxter_common/master/baxter_description/urdf/baxter.urdf",
                    meshes_url="https://raw.githubusercontent.com/RethinkRobotics/baxter_common/master/")