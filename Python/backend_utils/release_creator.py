import re
from subprocess import call, Popen
from pathlib import Path
from typing import List, Dict
from secrets import token_urlsafe
from dropbox import Dropbox
from dropbox.exceptions import ApiError
from tdw.backend.paths import EDITOR_LOG_PATH, PLAYER_LOG_PATH
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller
from tdw.output_data import OutputData
from tdw.version import __version__
from tdw.dev.config import Config
from tdw.dev.pypi_uploader import PyPiUploader
from tdw.dev.versions import versions_are_equal, VERSION_TDWUNITY, VERSION_UNITY_EDITOR
from tdw.dev.dockerizer import Dockerizer
from shutil import copyfile, rmtree, copytree
from github import Github, Repository
from argparse import ArgumentParser
from time import sleep
from os import chdir, getcwd


class ReleaseCreator:
    """
    Create standalone builds for TDW and upload them to the public tdw repo.
    See: Documentation/misc_backend/release_creator.md
    """

    # Each platform, its extension, and the command line argument.
    PLATFORMS = {"Windows": {"extension": ".exe", "call": ["-buildWindows64Player"]},
                 "OSX": {"extension": ".app", "call": ["-buildOSXUniversalPlayer"]},
                 "Linux": {"extension": ".x86_64", "call": ["-buildLinux64Player"]}}
    # Use this argument when calling Unity.
    PROJECT_PATH_ARG = "-projectPath"
    CONFIG: Config = Config()
    TDWUNITY_PATH = str(CONFIG.tdwunity_path.joinpath("TDWUnity").resolve())
    DEST_PATH = CONFIG.tdwunity_path.joinpath("bin")
    if not DEST_PATH.exists():
        DEST_PATH.mkdir(parents=True)

    @staticmethod
    def get_editor_path() -> str:
        """
        Returns the path to Unity Editor.
        """

        return f"C:/Program Files/Unity/Hub/Editor/{VERSION_UNITY_EDITOR}/Editor/Unity.exe"

    @staticmethod
    def get_unity_call() -> List[str]:
        """
        Returns the beginning of a Unity Editor call.
        """

        return [ReleaseCreator.get_editor_path(), "-quit", "-batchmode"]

    @staticmethod
    def create_platform_directories() -> (Path, Dict[str, Path]):
        """
        Create directories for each platform.
        """

        tdw_dir = f"TDW_v{VERSION_TDWUNITY}"

        release_path = ReleaseCreator.DEST_PATH.joinpath(tdw_dir)
        # Rebuild the release directory.
        if release_path.exists():
            rmtree(str(release_path.resolve()))
        release_path.mkdir(parents=True)
        platforms: Dict[str, Path] = {}
        for platform in ReleaseCreator.PLATFORMS:
            platform_root_directory = release_path.joinpath(platform)
            if not platform_root_directory.exists():
                platform_root_directory.mkdir()
            platforms.update({platform: platform_root_directory})
        print(f"Created platform directories for {tdw_dir}")
        return release_path, platforms

    @staticmethod
    def create_build(platform: str, platform_path: Path) -> None:
        """
        Create the build for a platform.

        :param platform: The platform directory.
        :param platform_path: The path to the platform directory.
        """

        build_path = platform_path.joinpath(f"TDW{ReleaseCreator.PLATFORMS[platform]['extension']}")

        build_call = ReleaseCreator.get_unity_call()[:]
        build_call.extend([ReleaseCreator.PROJECT_PATH_ARG,
                           ReleaseCreator.TDWUNITY_PATH])
        build_call.extend(ReleaseCreator.PLATFORMS[platform]["call"])
        build_call.append(str(build_path.resolve()))
        print(f"Creating build for {platform}...")
        call(build_call)

        # Check the log for any errors.
        if ReleaseCreator.check_editor_log_for_errors():
            print("...Done!")
        assert build_path.exists(), f"Failed to create build: {build_path}"

        # Add a text file with version info.
        platform_path.joinpath("version.txt").write_text(__version__, encoding="utf-8")

    @staticmethod
    def check_editor_log_for_errors() -> bool:
        """
        After running the Editor in batchmode, check the log for a compiler failure.
        """

        # If there is an editor log, read it.
        if EDITOR_LOG_PATH.exists():
            txt = EDITOR_LOG_PATH.read_text(encoding="utf-8")
            # If there is a compiler error, raise an exception.
            if "-----CompilerOutput:-stdout--exitcode: 1--compilationhadfailure: True" in txt \
                    or "Building Player failed" in txt:
                raise Exception(f"Compiler error. See: {EDITOR_LOG_PATH}")
        return True

    @staticmethod
    def reset_build_target() -> None:
        """
        Reset the build target to Windows.
        """

        build_call = ReleaseCreator.get_unity_call()[:]
        build_call.extend([ReleaseCreator.PROJECT_PATH_ARG,
                           ReleaseCreator.TDWUNITY_PATH])
        build_call.extend(["-executeMethod", "BuildTargeter.SetWindowsTarget"])
        call(build_call)
        print("Reset build target to Windows")

    @staticmethod
    def upload(assets: Dict[str, Path]) -> None:
        """
        Upload the assets as a new release.

        :param assets: The paths to each asset.
        """

        print("Uploading release to GitHub...")

        # A major release always ends in 0.
        major = VERSION_TDWUNITY.split(".")[-1] == "0"

        credentials = Path.home().joinpath("tdw_config/github_auth.txt").read_text(encoding="utf-8").strip()

        g = Github(credentials)
        repo: Repository = g.get_repo("threedworld-mit/tdw")

        # Check if a release with this version already exists.
        for release in repo.get_releases():
            if release.title == VERSION_TDWUNITY:
                release.delete_release()
                print("Deleted existing release.")
                break
        if major:
            message = f"**This is a major release.** There may be changes to the API that break or alter how your" \
                      f" code behaves.\n\n{ReleaseCreator.get_changelog(VERSION_TDWUNITY)}"
        else:
            version_family = VERSION_TDWUNITY.replace("." + VERSION_TDWUNITY.split(".")[-1], "")
            message = f"This is an incremental update to {version_family}. " \
                      f"If you are already using a {version_family} release, you can safely upgrade without " \
                      f"having to change any of your code.\n\n{ReleaseCreator.get_changelog(VERSION_TDWUNITY)}"
        # Create the release.
        release = repo.create_git_release(tag=VERSION_TDWUNITY,
                                          name=VERSION_TDWUNITY,
                                          message=message,
                                          prerelease=False,
                                          target_commitish="master",
                                          draft=False)
        print("Created new release.")
        # Upload the assets.
        for asset in assets:
            if assets[asset].suffix == ".zip":
                mime_type = "application/zip"
            elif assets[asset].suffix == ".gz":
                mime_type = "application/gzip"
            else:
                raise Exception(f"Unexpected file suffix: {assets[asset]}")
            release.upload_asset(path=str(assets[asset].resolve()),
                                 name=assets[asset].name,
                                 content_type=mime_type)
            print(f"Uploaded: {assets[asset].name}")

        # Add tags to each repo.
        for path in [ReleaseCreator.CONFIG.tdw_path, ReleaseCreator.CONFIG.tdwunity_path, ReleaseCreator.CONFIG.tdw_docs_path]:
            chdir(str(path))
            call(["git", "tag", VERSION_TDWUNITY])
            call(["git", "push", "origin", VERSION_TDWUNITY])

    @staticmethod
    def verify(windows_directory: Path) -> None:
        """
        After creating the Windows build, verify that it is OK (in particular that there are no post-process errors).

        :param windows_directory: The directory of the Windows build.
        """

        build_path = windows_directory.joinpath("TDW.exe")
        assert build_path.exists(), f"TDW.exe not found!"

        # Launch the build.
        Popen([str(build_path.resolve())])

        # Launch the controller.
        c = Controller(launch_build=False)
        # Create a simple scene and capture an image.
        commands = [TDWUtils.create_empty_room(12, 12)]
        commands.extend(TDWUtils.create_avatar(position={"x": 0, "y": 2, "z": 0}, look_at=TDWUtils.VECTOR3_ZERO))
        commands.extend([{"$type": "set_pass_masks",
                          "pass_masks": ["_img"]},
                         {"$type": "send_images",
                          "frequency": "once"}])
        resp = c.communicate(commands)
        # Terminate the build.
        c.communicate({"$type": "terminate"})

        # Terminate the controller.
        c.socket.close()

        # Verify that we received an image.
        assert len(resp) == 2, f"Did not receive any image data: {resp}"
        r_id = OutputData.get_data_type_id(resp[0])
        assert r_id == "imag", f"Expected image but got: {r_id}"

        # Verify that there are no exceptions in the player log.
        txt = PLAYER_LOG_PATH.read_text(encoding="utf-8")
        exceptions = ""
        for line in txt.split("\n"):
            if "exception" in line.lower() or "error" in line.lower():
                exceptions += "\n" + line
        if exceptions != "":
            raise Exception(exceptions)
        # Wait a bit so that the directory is writeable again.
        sleep(6)

    @staticmethod
    def path_to_wsl(path: Path) -> str:
        """
        :param path: A Pathlib object.

        :return: A string representation of the path, converted from Windows to WSL 2 (e.g. C:\\ -> /mnt/c)
        """

        return str(path.resolve()).replace("\\", "/").replace("C:/", "/mnt/c/").replace("D:/", "/mnt/d/")

    @staticmethod
    def get_changelog(version: str) -> str:
        """
        :param version: The TDW version.

        :return: The changelog for this version.
        """

        version_split = [int(v) for v in version.split(".")]
        # This is a major release.
        if version_split[-1] == 0:
            re_suffix = r"^# "
        # This is a minor release.
        else:
            re_suffix = r"^## "
        # Open the changelog.
        changelog = ReleaseCreator.CONFIG.tdw_docs_path.joinpath("docs/changelog.md").read_text()
        # Get the changelog for this release.
        return re.search("(## v" + version.replace(".", r"\.") + r"((.|\n)*?))" + re_suffix, changelog,
                         flags=re.MULTILINE).group(2).strip()


if __name__ == "__main__":
    equal, all_versions = versions_are_equal()
    print(all_versions)
    if not equal:
        print("ERROR! Versions are not the same.")
        exit()
    print("Versions are all the same. Continuing...")
    parser = ArgumentParser()
    parser.add_argument("--no_upload", action="store_true", help="Don't automatically upload.")
    parser.add_argument("--no_docker", action="store_true", help="Don't build or push a Docker container.")
    parser.add_argument("--no_zip", action="store_true", help="Don't create a .zip or .tar.gz file.")
    parser.add_argument("--no_test", action="store_true", help="Don't test the Windows build.")
    parser.add_argument("--platform", type=str, choices=["all", "windows", "osx", "linux"], default="all",
                        help="Target platform")
    parser.add_argument("--dropbox", default=None, type=str,
                        help="If not None, rename the zip file to with the value as the suffix of the filename and "
                             "upload to TDW_Shared/test_builds on Dropbox. "
                             "For example, --dropbox test will upload TDW_Linux.tar.gz to "
                             "TDW_Shared/test_builds/TDW_Linux_test.tar.gz")
    args = parser.parse_args()

    release_directory, platform_directories = ReleaseCreator.create_platform_directories()

    zip_files: Dict[str, Path] = {}

    for platform_dir in platform_directories:
        # Build only the selected platform.
        if args.platform != "all" and platform_dir.lower() != args.platform:
            continue

        # Set the build target to Windows. Otherwise, the compiler will have XR errors.
        if platform_dir == "Windows":
            ReleaseCreator.reset_build_target()

        # Create the build.
        ReleaseCreator.create_build(platform_dir, platform_directories[platform_dir])

        if platform_dir == "Windows":
            # Copy the Oculus audio spatializer .dll file.
            oculus_audio_spatializer_src = ReleaseCreator.CONFIG.tdwunity_path.joinpath(
                "TDWBase/Assets/Oculus/Spatializer/Plugins/x86_64/AudioPluginOculusSpatializer.dll")
            oculus_audio_spatializer_dst = release_directory.joinpath(
                "Windows/TDW_Data/Plugins/x86_64/AudioPluginOculusSpatializer.dll")
            copyfile(src=str(oculus_audio_spatializer_src.resolve()), dst=str(oculus_audio_spatializer_dst.resolve()))
            # Verify.
            if not args.no_test:
                ReleaseCreator.verify(platform_directories[platform_dir])

        platform_directory = release_directory.joinpath(platform_dir)
        # Run chmod +x for Linux and OS X.
        if platform_dir == "Linux" or platform_dir == "OSX":
            if platform_dir == "Linux":
                executable_path = platform_directory.joinpath("TDW.x86_64")
            else:
                executable_path = platform_directory.joinpath("TDW.app/Contents/MacOS/TDW")
            call(["wsl", "chmod", "+x", ReleaseCreator.path_to_wsl(executable_path)])
        # Rename the directory to TDW/
        platform_directory.replace(release_directory.joinpath("TDW"))
        # Delete the Burst folder.
        burst = release_directory.joinpath("TDW").joinpath("TDW_BurstDebugInformation_DoNotShip")
        if burst.exists():
            rmtree(str(burst.resolve()))
        # Change directory in preparation for copying.
        cwd = getcwd()
        chdir(str(release_directory.resolve()))
        tdwunity_assets = ReleaseCreator.CONFIG.tdwunity_path.joinpath("TDWUnity/Assets")
        # Copy files.
        if platform_dir == "OSX":
            # Copy the Resonance Audio .bundle plugin file.
            resonance_audio_src = tdwunity_assets.joinpath(
                "ResonanceAudio/Plugins/x86_64/audiopluginresonanceaudio.bundle")
            resonance_audio_dst = release_directory.joinpath(
                "TDW/TDW.app/Contents/PlugIns/audiopluginresonanceaudio.bundle")
            copyfile(src=str(resonance_audio_src.resolve()), dst=str(resonance_audio_dst.resolve()))
            # Copy the Oculus audio spatializer .bundle directory.
            oculus_audio_spatializer_src = tdwunity_assets.joinpath(
                "Oculus/Spatializer/Plugins/AudioPluginOculusSpatializer.bundle")
            oculus_audio_spatializer_dst = release_directory.joinpath(
                "TDW/TDW.app/Contents/PlugIns/AudioPluginOculusSpatializer.bundle")
            copytree(src=str(oculus_audio_spatializer_src.resolve()), dst=str(oculus_audio_spatializer_dst.resolve()))
            # Copy fast_image_encoder.
            fast_image_encoder_src = tdwunity_assets.joinpath(
                "FastImageEncoder/libfast_image_encoder.dylib")
            fast_image_encoder_dst = release_directory.joinpath(
                "TDW/TDW.app/Contents/PlugIns/libfast_image_encoder.dylib")
            copyfile(src=str(fast_image_encoder_src.resolve()), dst=str(fast_image_encoder_dst.resolve()))
            # Create a shellscript as a workaround for OS X.
            bash_path = release_directory.joinpath("TDW/setup.sh")
            bash_path.write_text("xattr -r -d com.apple.quarantine TDW.app")
            call(["wsl", "chmod", "+x", ReleaseCreator.path_to_wsl(bash_path)])
        elif platform_dir == "Linux":
            fast_image_encoder_src = tdwunity_assets.joinpath(
                "FastImageEncoder/libfast_image_encoder.so")
            fast_image_encoder_dst = release_directory.joinpath(
                "TDW/TDW_Data/Plugins/libfast_image_encoder.so")
            copyfile(src=str(fast_image_encoder_src.resolve()), dst=str(fast_image_encoder_dst.resolve()))
        if not args.no_zip:
            # Create a .zip file for the Windows build.
            if platform_dir == "Windows":
                filename = f"TDW_{platform_dir}.zip"
                call(["wsl", "zip", "-rm", filename, "TDW"])
            # Create a .tar.gz file for the OS X and Linux build so that we can preserve file permissions.
            else:
                filename = f"TDW_{platform_dir}.tar.gz"
                print(f"Creating {filename}")
                call(["wsl", "tar", "czfp", filename, "-C", ReleaseCreator.path_to_wsl(release_directory), "TDW"])
                print("...Done!")
                rmtree("TDW")
                print("Deleted uncompressed files.")
            # Remember the zip file path for when it's time to upload.
            zip_files.update({platform_dir: release_directory.joinpath(filename)})
        chdir(cwd)
    # Reset the Unity build target.
    ReleaseCreator.reset_build_target()

    # Upload the files.
    if not args.no_upload:
        ReleaseCreator.upload(zip_files)
        # Update the pip module.
        PyPiUploader.run(False)
        # Build and push a new Docker image.
        if not args.no_docker:
            Dockerizer.build(push=True)
    else:
        # Upload to dropbox.
        if args.dropbox is not None:
            dropbox_token = re.search(r"token=(.*)", Path.home().joinpath("tdw_config/dropbox.txt").read_text(),
                                      flags=re.MULTILINE).group(1)
            dbx = Dropbox(dropbox_token, timeout=None)
            # Add this identifier if needed.
            file_token = token_urlsafe(4)
            print("Uploading to dropbox...")
            for k in zip_files:
                # Append the suffix identifer.
                dst_path = str(zip_files[k].resolve()).replace(f"TDW_{k}", f"TDW_{k}_{args.dropbox}")
                dropbox_filename = Path(dst_path).name
                zip_files[k].replace(Path(dst_path))
                dropbox_path = f"/TDW_Shared/test_builds/{dropbox_filename}"
                # Check if the file exists. If it does, append some random characters.
                file_exists: bool = True
                try:
                    dbx.files_get_metadata(dropbox_path)
                except ApiError:
                    file_exists = False
                if file_exists:
                    dropbox_filename = zip_files[k].name.replace(f"TDW_{k}", f"TDW_{k}_{args.dropbox}_{file_token}")
                    dropbox_path = f"/TDW_Shared/test_builds/{dropbox_filename}"
                # Upload the file and generate a shareable link.
                dbx.files_upload(Path(dst_path).read_bytes(), dropbox_path)
                dropbox_shared_link = dbx.sharing_create_shared_link_with_settings(dropbox_path).url
                print(dropbox_shared_link)
            dbx.close()
    print("DONE!")
