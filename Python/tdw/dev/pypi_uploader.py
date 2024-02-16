from os import chdir
from subprocess import call
from distutils import dir_util
from tdw import __version__
from tdw.backend.update import Update
from tdw.dev.config import Config


class PyPiUploader:
    """
    Update the tdw Python module to PyPi. Requires TDW PyPi credentials.
    """

    @staticmethod
    def run(test: bool) -> bool:
        """
        Upload to PyPi.

        :param test: If True, upload to TestPyPi. If False, upload to PyPi.
        """

        # Check if the version number in setup.py matches the latest version on PyPi.
        v_pypi = Update.get_pypi_version()
        if v_pypi == __version__:
            print(f"PyPi and setup.py versions are both {v_pypi}; will not upload tdw to PyPi.")
            return False
        print(f"Uploading {__version__} to PyPi.")

        tdw_path = Config().tdw_path
        py_path = tdw_path.joinpath("Python")

        # Remove an existing dist.
        dist = py_path.joinpath("dist")
        if dist.exists():
            dir_util.remove_tree(str(dist.resolve()))
        # Create a new dist.
        chdir(str(py_path.resolve()))
        call(["py", "-3", "setup.py", "sdist"])
        # Upload the pip module to PyPi.
        if not test:
            call(["py", "-3", "-m", "twine", "upload", "dist/*"])
        else:
            call(["py", "-3", "-m", "twine", "upload", "--repository", "testpypi", "dist/*"])
        return True


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Upload to TestPyPi")
    args = parser.parse_args()
    PyPiUploader.run(args.test)
