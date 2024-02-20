from os import chdir, getcwd
from subprocess import call
from packaging import version
from tdw.version import __version__
from tdw.dev.config import Config


class Dockerizer:
    """
    Dockerize TDW.
    """

    @staticmethod
    def build(push: bool = True) -> None:
        """
        Build and push a Docker container.

        :param push: If True, push the container to DockerHub.
        """

        v = version.parse(__version__).release
        v = ".".join([str(q) for q in v[:-1]])

        tag = f"alters/tdw:{v}"

        cwd = getcwd()
        # Go to the directory.
        chdir(Config().tdw_path.joinpath("Docker"))
        # Build.
        call(["docker",
              "build",
              "-t", tag,
              "--build-arg", f"TDW_VERSION={v}",
              "."])
        # Push.
        if push:
            call(["docker",
                  "push",
                  tag])
        # Revert to the original directory.
        chdir(cwd)


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--push", action="store_true", help="Push to DockerHub")
    args = parser.parse_args()
    Dockerizer.build(args.push)
